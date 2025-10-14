from __future__ import annotations

import threading
import time
import random
from multiprocessing import Queue

from .http import SimpleHttpClient
from .metrics import Metrics
from .logger import RequestLogger


class TokenWorker:
    def __init__(self, cfg: dict):
        self.url = cfg["url"]
        self.method = (cfg.get("method", "POST") or "POST").upper()
        self.verify_tls = bool(cfg.get("verify_tls", True))
        self.timeout = float(int(cfg.get("timeout_ms", 30000)) / 1000.0)
        self.retries = int(cfg.get("retries", 0))
        self.backoff_ms = int(cfg.get("backoff_ms", 200))
        self.backoff_max_ms = int(cfg.get("backoff_max_ms", 2000))
        self.jitter_ms = int(cfg.get("jitter_ms", 100))
        retry_list = cfg.get("retry_on_statuses")
        if isinstance(retry_list, list):
            try:
                self.retry_on_statuses = {int(x) for x in retry_list}
            except Exception:
                self.retry_on_statuses = {0, 429}
        else:
            self.retry_on_statuses = {0, 429}
        # Deliberately import locally to avoid circular from users importing worker directly
        from .http import build_headers_and_body

        self.headers, self.data_bytes = build_headers_and_body(cfg)

    def step(self, http: SimpleHttpClient, metrics: Metrics, logger: RequestLogger | None = None, 
             thread_id: int = 0, request_num: int = 0):
        attempts = self.retries + 1
        delay_s = self.backoff_ms / 1000.0
        final_status, final_ms, final_err = 0, 0, None
        
        for i in range(attempts):
            # If logger is enabled, capture full response details
            if logger and logger.enabled:
                result = http.request(self.method, self.url, self.headers, self.data_bytes, 
                                    timeout=self.timeout, capture_response=True)
                final_status = result['status']
                final_ms = result['latency_ms']
                final_err = result['error']
                
                # Log the request/response
                logger.log_request(
                    thread_id=thread_id,
                    request_num=request_num,
                    method=self.method,
                    url=self.url,
                    headers=self.headers,
                    body=self.data_bytes,
                    status_code=final_status,
                    latency_ms=final_ms,
                    response_headers=result.get('response_headers'),
                    response_body=result.get('response_body'),
                    error=final_err,
                )
            else:
                status, ms, err = http.request(self.method, self.url, self.headers, self.data_bytes, timeout=self.timeout)
                final_status, final_ms, final_err = status, ms, err
            
            retryable = (final_status in self.retry_on_statuses) or (final_status >= 500)
            if retryable and i < attempts - 1:
                jitter_s = random.uniform(-self.jitter_ms, self.jitter_ms) / 1000.0
                time.sleep(max(0.0, delay_s + jitter_s))
                delay_s = min(delay_s * 2.0, self.backoff_max_ms / 1000.0)
                continue
            break
        metrics.add(final_status, final_ms, error=final_err)
        return final_status, final_ms, final_err


class TokenBucket:
    def __init__(self, rate_per_sec: float, capacity: int | None = None):
        self.rate = float(rate_per_sec)
        self.capacity = int(capacity or max(1, int(rate_per_sec)) or 1)
        self.tokens = self.capacity
        self.ts = time.perf_counter()
        self.lock = threading.Lock()

    def take(self, n: int = 1) -> bool:
        with self.lock:
            now = time.perf_counter()
            elapsed = now - self.ts
            self.ts = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            if self.tokens >= n:
                self.tokens -= n
                return True
            return False


def worker_process(proc_idx: int, cfg: dict, duration_s: int, threads: int, rps_share: float, queue_out: Queue, logger: RequestLogger | None = None):
    """Worker function running in single process with multiple threads."""
    print(f"[OK] Starting {threads} threads...", flush=True)
    if logger and logger.enabled:
        print(f"[OK] Detailed logging enabled: {logger.log_file}", flush=True)
    
    metrics = Metrics()
    stop_time = time.time() + duration_s
    last_update = time.time()
    tb = TokenBucket(rate_per_sec=rps_share, capacity=max(1, int(rps_share)) if rps_share > 0 else 1)

    try:
        worker = TokenWorker(cfg)
        print(f"[OK] Worker initialized: {worker.url}\n", flush=True)
    except Exception as e:
        print(f"[ERROR] initializing worker: {e}", flush=True)
        queue_out.put(("done", proc_idx, metrics.snapshot()))
        return

    def thread_fn(ti: int):
        """Thread worker function with proper exception handling."""
        nonlocal last_update
        print(f"[Thread {ti:02d}] Started", flush=True)
        http = SimpleHttpClient(verify_tls=worker.verify_tls, user_agent=f"pystress/1.0 t{ti}")
        req_count = 0
        first_status = None
        
        try:
            while time.time() < stop_time:
                if rps_share <= 0 or tb.take(1):
                    try:
                        req_count += 1
                        status, ms, err = worker.step(http, metrics, logger, ti, req_count)
                        
                        if req_count == 1:
                            first_status = status
                            print(f"[Thread {ti:02d}] First request: Status={first_status}, Latency={ms}ms", flush=True)

                        now = time.time()
                        if now - last_update >= 5.0:
                            last_update = now
                            snapshot = metrics.snapshot()
                            queue_out.put(("progress", proc_idx, snapshot))
                            
                    except Exception as e:
                        print(f"[Thread {ti:02d}] Request error: {type(e).__name__}: {e}", flush=True)
                        metrics.add(0, 0, error=f"request_error:{type(e).__name__}")
                else:
                    time.sleep(0.001)
        except Exception as e:
            print(f"[Thread {ti:02d}] Fatal error: {type(e).__name__}: {e}", flush=True)
            metrics.add(0, 0, error=f"thread_fatal:{type(e).__name__}")
        finally:
            print(f"[Thread {ti:02d}] Finished - {req_count} requests", flush=True)

    ts = []
    for ti in range(max(1, threads)):
        th = threading.Thread(target=thread_fn, args=(ti,), daemon=True, name=f"Worker-{ti}")
        th.start()
        ts.append(th)
    
    for th in ts:
        th.join()

    final_snapshot = metrics.snapshot()
    print(f"\n[OK] All threads completed: {final_snapshot['total']} total requests\n", flush=True)
    queue_out.put(("done", proc_idx, final_snapshot))
