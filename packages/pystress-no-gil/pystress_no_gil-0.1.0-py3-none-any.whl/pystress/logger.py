from __future__ import annotations

import threading
import time
from datetime import datetime
from pathlib import Path


class RequestLogger:
    """Thread-safe logger for detailed request/response logging."""
    
    def __init__(self, log_file: str | None = None):
        self.log_file = log_file
        self.enabled = log_file is not None
        self.lock = threading.Lock()
        self.request_count = 0
        
        if self.enabled:
            # Create parent directory if needed
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize log file with header
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("=" * 100 + "\n")
                f.write(f"PYSTRESS DETAILED REQUEST LOG\n")
                f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 100 + "\n\n")
    
    def log_request(
        self,
        thread_id: int,
        request_num: int,
        method: str,
        url: str,
        headers: dict,
        body: bytes | None,
        status_code: int,
        latency_ms: int,
        response_headers: dict | None = None,
        response_body: str | None = None,
        error: str | None = None,
    ):
        """Log a complete request/response cycle."""
        if not self.enabled:
            return
        
        with self.lock:
            self.request_count += 1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'=' * 100}\n")
                f.write(f"REQUEST #{self.request_count} | Thread {thread_id:02d} | Request #{request_num}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"{'=' * 100}\n\n")
                
                # Request details
                f.write(f">>> REQUEST:\n")
                f.write(f"{method} {url}\n")
                f.write(f"Latency: {latency_ms}ms ({latency_ms/1000:.3f}s)\n\n")
                
                # Request headers
                f.write(f"Request Headers:\n")
                for key, value in headers.items():
                    # Mask sensitive headers
                    if key.lower() in ('authorization', 'cookie', 'x-api-key'):
                        value = f"***MASKED*** (length: {len(str(value))})"
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
                
                # Request body
                if body:
                    f.write(f"Request Body ({len(body)} bytes):\n")
                    try:
                        body_str = body.decode('utf-8')[:1000]  # Limit to 1000 chars
                        if len(body) > 1000:
                            body_str += f"\n... (truncated, total {len(body)} bytes)"
                        f.write(f"{body_str}\n\n")
                    except Exception:
                        f.write(f"<binary data, {len(body)} bytes>\n\n")
                else:
                    f.write(f"Request Body: <empty>\n\n")
                
                # Response details
                f.write(f"<<< RESPONSE:\n")
                if error:
                    f.write(f"Status: ERROR - {error}\n")
                    f.write(f"Status Code: {status_code}\n\n")
                else:
                    f.write(f"Status Code: {status_code}\n\n")
                
                # Response headers
                if response_headers:
                    f.write(f"Response Headers:\n")
                    for key, value in response_headers.items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
                
                # Response body
                if response_body:
                    f.write(f"Response Body ({len(response_body)} bytes):\n")
                    body_preview = response_body[:1000]  # Limit to 1000 chars
                    if len(response_body) > 1000:
                        body_preview += f"\n... (truncated, total {len(response_body)} bytes)"
                    f.write(f"{body_preview}\n\n")
                
                f.write(f"{'-' * 100}\n")
    
    def close(self):
        """Write footer to log file."""
        if self.enabled:
            with self.lock:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n{'=' * 100}\n")
                    f.write(f"LOG COMPLETED\n")
                    f.write(f"Total Requests Logged: {self.request_count}\n")
                    f.write(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"{'=' * 100}\n")

