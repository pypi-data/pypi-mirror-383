from __future__ import annotations

import base64
import json
import time
import urllib.parse

try:
    import urllib3
    from urllib3.exceptions import HTTPError as Urllib3HTTPError
    HAS_URLLIB3 = True
except ImportError:
    HAS_URLLIB3 = False
    # Fallback to stdlib
    import urllib.request
    import urllib.error
    import ssl
    import http.cookiejar

from .metrics import Metrics  # for typing friendliness in some users


def now_ms() -> int:
    return int(time.perf_counter() * 1000)


class SimpleHttpClient:
    """
    HTTP client with connection pooling support.
    
    Uses urllib3 if available (recommended for high concurrency),
    falls back to urllib.request if not installed.
    """
    
    def __init__(self, verify_tls: bool = True, user_agent: str | None = None, max_connections: int = 1000):
        self.user_agent = user_agent or "pystress/1.0"
        self.verify_tls = verify_tls
        
        if HAS_URLLIB3:
            # urllib3 with connection pooling - much better for high concurrency
            self.http = urllib3.PoolManager(
                num_pools=50,  # Pools per host
                maxsize=max_connections,  # Connections per pool
                retries=False,  # We handle retries ourselves
                cert_reqs='CERT_REQUIRED' if verify_tls else 'CERT_NONE',
                timeout=urllib3.Timeout(connect=10.0, read=30.0)
            )
            if not verify_tls:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.backend = "urllib3"
        else:
            # Fallback to stdlib urllib.request (no pooling)
            self.cj = http.cookiejar.CookieJar()
            handlers = [urllib.request.HTTPCookieProcessor(self.cj)]
            if not verify_tls:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                handlers.append(urllib.request.HTTPSHandler(context=ctx))
            self.opener = urllib.request.build_opener(*handlers)
            self.backend = "urllib.request"

    def request(self, method: str, url: str, headers: dict | None = None,
                data: bytes | None = None, timeout: float = 30.0, capture_response: bool = False):
        """
        Make an HTTP request.
        
        Returns:
            If capture_response=True: dict with status, latency_ms, error, response_headers, response_body
            If capture_response=False: tuple (status_code, latency_ms, error_string)
        """
        all_headers = {"User-Agent": self.user_agent}
        if headers:
            all_headers.update(headers)
        
        if HAS_URLLIB3:
            return self._request_urllib3(method, url, all_headers, data, timeout, capture_response)
        else:
            return self._request_stdlib(method, url, all_headers, data, timeout, capture_response)
    
    def _request_urllib3(self, method: str, url: str, headers: dict, 
                         data: bytes | None, timeout: float, capture_response: bool):
        """urllib3 backend with connection pooling."""
        result = {
            'status': 0,
            'latency_ms': 0,
            'error': None,
            'response_headers': None,
            'response_body': None,
        }
        
        t0 = now_ms()
        try:
            resp = self.http.request(
                method.upper(), 
                url,
                body=data,
                headers=headers,
                timeout=timeout,
                preload_content=True,
                retries=False
            )
            ms = now_ms() - t0
            result['status'] = resp.status
            result['latency_ms'] = ms
            
            if capture_response:
                result['response_headers'] = dict(resp.headers)
                try:
                    result['response_body'] = resp.data.decode('utf-8')
                except Exception:
                    result['response_body'] = f"<binary data, {len(resp.data)} bytes>"
                return result
            
            return resp.status, ms, None
            
        except urllib3.exceptions.HTTPError as e:
            ms = now_ms() - t0
            # urllib3 exceptions don't have status codes readily available
            result['status'] = 0
            result['latency_ms'] = ms
            result['error'] = f"HTTPError:{type(e).__name__}"
            
            if capture_response:
                return result
            return 0, ms, f"HTTPError:{type(e).__name__}"
            
        except Exception as e:
            ms = now_ms() - t0
            result['status'] = 0
            result['latency_ms'] = ms
            result['error'] = f"Exception:{type(e).__name__}"
            
            if capture_response:
                return result
            return 0, ms, f"Exception:{type(e).__name__}"
    
    def _request_stdlib(self, method: str, url: str, headers: dict,
                       data: bytes | None, timeout: float, capture_response: bool):
        """Stdlib urllib.request fallback (no connection pooling)."""
        req = urllib.request.Request(url=url, data=data, method=method.upper())
        for k, v in headers.items():
            req.add_header(k, v)
        
        result = {
            'status': 0,
            'latency_ms': 0,
            'error': None,
            'response_headers': None,
            'response_body': None,
        }
        
        t0 = now_ms()
        try:
            with self.opener.open(req, timeout=timeout) as resp:
                body = resp.read()
                ms = now_ms() - t0
                result['status'] = resp.status
                result['latency_ms'] = ms
                
                if capture_response:
                    result['response_headers'] = dict(resp.headers)
                    try:
                        result['response_body'] = body.decode('utf-8')
                    except Exception:
                        result['response_body'] = f"<binary data, {len(body)} bytes>"
                    return result
                
                return resp.status, ms, None
                
        except urllib.error.HTTPError as e:
            body = e.read() if hasattr(e, "read") else b""
            ms = now_ms() - t0
            result['status'] = e.code
            result['latency_ms'] = ms
            result['error'] = f"HTTPError:{e.code}"
            
            if capture_response:
                result['response_headers'] = dict(e.headers) if hasattr(e, 'headers') else {}
                try:
                    result['response_body'] = body.decode('utf-8')
                except Exception:
                    result['response_body'] = f"<binary data, {len(body)} bytes>"
                return result
            
            return e.code, ms, f"HTTPError:{e.code}"
            
        except Exception as e:
            ms = now_ms() - t0
            result['status'] = 0
            result['latency_ms'] = ms
            result['error'] = f"Exception:{type(e).__name__}"
            
            if capture_response:
                return result
            return 0, ms, f"Exception:{type(e).__name__}"


def build_headers_and_body(cfg: dict) -> tuple[dict, bytes | None]:
    headers = dict(cfg.get("headers") or {})
    if not any(h.lower() == "authorization" for h in headers):
        ba = cfg.get("basic_auth")
        if ba and isinstance(ba, dict) and "username" in ba and "password" in ba:
            raw = f"{ba['username']}:{ba['password']}".encode()
            headers["Authorization"] = "Basic " + base64.b64encode(raw).decode()

    method = (cfg.get("method", "POST") or "POST").upper()
    data_bytes = None
    if method in ("POST", "PUT", "PATCH", "DELETE"):
        if "json" in cfg and cfg["json"] is not None:
            data_bytes = json.dumps(cfg["json"]).encode()
            if not any(h.lower() == "content-type" for h in headers):
                headers["Content-Type"] = "application/json"
        elif "form" in cfg and cfg["form"] is not None:
            data_bytes = urllib.parse.urlencode(cfg["form"]).encode()
            if not any(h.lower() == "content-type" for h in headers):
                headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif "body" in cfg and cfg["body"] is not None:
            data_bytes = str(cfg["body"]).encode()
    return headers, data_bytes
