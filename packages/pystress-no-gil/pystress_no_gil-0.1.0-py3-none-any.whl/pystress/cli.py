from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import cpu_count, get_context
from pathlib import Path
import threading

from .http import now_ms, SimpleHttpClient, build_headers_and_body
from .metrics import Metrics
from .worker import worker_process
from .report import generate_html_report
from .logger import RequestLogger


def check_python_version():
    """Check if Python 3.14+ with GIL disabled is being used."""
    version_info = sys.version_info
    python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    print("\n" + "=" * 80)
    print(" " * 25 + "PYSTRESS REQUIREMENTS CHECK")
    print("=" * 80)
    print(f"Python Version: {python_version}")
    print(f"Python Executable: {sys.executable}")
    
    # Check Python version
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 14):
        print("\n" + "[X] " * 40)
        print("ERROR: Python 3.14 or higher is required!")
        print("=" * 80)
        print("\nPyStress requires Python 3.14+ with free-threading support (no GIL).")
        print(f"Current version: Python {python_version}")
        print("\n[GUIDE] To install Python 3.14t (free-threaded):")
        print("=" * 80)
        print("""
1. Clone and build Python 3.14 with free-threading:
   git clone https://github.com/python/cpython.git
   cd cpython
   git checkout 3.14
   
   # Linux/Mac:
   ./configure --disable-gil --prefix=/opt/python3.14t
   make -j$(nproc)
   sudo make install
   
   # Windows:
   PCbuild\\build.bat --disable-gil -c Release

2. Verify installation:
   python3.14t -c "import sys; print(sys.version, sys._is_gil_enabled())"
   
3. Install PyStress with Python 3.14t:
   python3.14t -m pip install -e .
   
4. Run PyStress:
   python3.14t -m pystress --config your_config.json
        """)
        print("=" * 80)
        print("\n[LINK] More info: https://docs.python.org/3.14/howto/free-threading-python.html")
        print("=" * 80)
        sys.exit(1)
    
    # Check GIL status
    gil_enabled = True
    gil_status = "[!] ENABLED (Limited Parallelism)"
    
    if hasattr(sys, '_is_gil_enabled'):
        gil_enabled = sys._is_gil_enabled()
        if not gil_enabled:
            gil_status = "[OK] DISABLED (Free-threaded Mode)"
    
    print(f"GIL Status: {gil_status}")
    
    if gil_enabled:
        print("\n" + "[!] " * 40)
        print("WARNING: GIL is ENABLED - You won't get true parallelism!")
        print("=" * 80)
        print("\nYou're running Python 3.14+, but GIL is still enabled.")
        print("For maximum performance, use Python 3.14t (free-threaded build).")
        print("\n[TIP] To enable free-threading:")
        print("   1. Build Python with --disable-gil flag")
        print("   2. Or download pre-built free-threaded Python binaries")
        print("   3. Verify with: python3.14t -c 'import sys; print(sys._is_gil_enabled())'")
        print("      Should print: False")
        print("\n[!] Continuing anyway, but performance will be limited by GIL...")
        print("=" * 80)
        
        # Give user time to read the warning
        print("\nPress Ctrl+C to abort, or wait 5 seconds to continue...")
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n\nAborted by user.")
            sys.exit(1)
    else:
        print("[OK] All requirements met! True parallelism enabled.")
    
    print("=" * 80 + "\n")
    
    return not gil_enabled


def acquire_token(token_cfg: dict) -> str | None:
    print("\n" + "=" * 60)
    print("ACQUIRING ACCESS TOKEN")
    print("=" * 60)
    print(f"Token URL: {token_cfg.get('url')}")
    print("Requesting token...", flush=True)

    http = SimpleHttpClient(verify_tls=token_cfg.get('verify_tls', True))
    headers, data_bytes = build_headers_and_body(token_cfg)
    method = token_cfg.get('method', 'POST')
    timeout = float(token_cfg.get('timeout_ms', 30000)) / 1000.0

    try:
        # Use the unified request() method that handles both urllib3 and urllib.request
        result = http.request(
            method=method,
            url=token_cfg['url'],
            headers=headers,
            data=data_bytes,
            timeout=timeout,
            capture_response=True
        )
        
        status_code = result['status']
        print(f"  HTTP Status: {status_code}")
        
        if status_code == 200 and result['response_body']:
            data = json.loads(result['response_body'])
            token = data.get('access_token')
            if token:
                print(f"[OK] Token acquired successfully (length: {len(token)})")
                print(f"  Token type: {data.get('token_type', 'N/A')}")
                print(f"  Expires in: {data.get('expires_in', 'N/A')}s")
                print("=" * 60)
                return token
            else:
                print("[FAIL] No access_token in response")
                print(f"Response: {result['response_body'][:200]}")
                return None
        else:
            print(f"[FAIL] HTTP {status_code}")
            if result['response_body']:
                print(f"Response: {result['response_body'][:200]}")
            if result['error']:
                print(f"Error: {result['error']}")
            return None
            
    except Exception as e:
        print(f"[FAIL] Failed to acquire token: {e}")
        return None


def print_summary(args, merged: Metrics, threads: int, baseline_stats: dict, start_wall: float):
    total_elapsed = max(1, time.time() - start_wall)
    snap = merged.snapshot()
    actual_rps = snap['total'] / total_elapsed

    total_requests = snap['total']
    passed_requests = snap['ok']
    failed_requests = total_requests - passed_requests
    pass_rate = (passed_requests / total_requests * 100) if total_requests > 0 else 0
    fail_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0

    min_sec = snap['min_ms'] / 1000.0
    max_sec = snap['max_ms'] / 1000.0
    avg_sec = snap['avg_ms'] / 1000.0
    p50_sec = snap['p50_ms'] / 1000.0
    p90_sec = snap['p90_ms'] / 1000.0
    p99_sec = snap['p99_ms'] / 1000.0

    print("\n" + "=" * 80)
    print(" " * 28 + "PYSTRESS SUMMARY")
    print("=" * 80)

    print("\n[TEST OVERVIEW]")
    print("-" * 80)
    print(f"  Duration:              {total_elapsed:.2f}s (target: {args.duration}s)")
    print(f"  Total Requests:        {snap['total']}")
    print(f"  [OK] Passed (2xx-3xx): {passed_requests} ({pass_rate:.2f}%)")
    print(f"  [X] Failed (4xx/5xx):  {failed_requests} ({fail_rate:.2f}%)")

    print("\n[THROUGHPUT]")
    print("-" * 80)
    print(f"  Actual RPS:            {actual_rps:.2f} req/s")
    if threads > 0:
        print(f"  Requests/Thread:       {snap['total']/threads:.1f}")

    # Get physical cores info
    try:
        import psutil
        physical_cores = psutil.cpu_count(logical=False)
    except:
        physical_cores = cpu_count()
    
    logical_processors = cpu_count()
    
    print("\n[PARALLELISM & HARDWARE]")
    print("-" * 80)
    print(f"  Physical CPU Cores:    {physical_cores}")
    print(f"  Logical Processors:    {logical_processors} ({logical_processors//physical_cores}x hyperthreading)" if logical_processors > physical_cores else f"  Logical Processors:    {logical_processors} (no hyperthreading)")
    print(f"  Worker Threads:        {threads}")
    print(f"  GIL Status:            {'[OK] DISABLED - {threads} threads execute in parallel' if hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled() else '[!] ENABLED - Only 1 thread executes at a time'}")

    print("\n[LATENCY COMPARISON]")
    print("=" * 80)
    if baseline_stats:
        baseline_avg_sec = baseline_stats['avg'] / 1000.0
        baseline_min_sec = baseline_stats['min'] / 1000.0
        baseline_max_sec = baseline_stats['max'] / 1000.0

        print(f"\n{'Metric':<20} {'Quick Baseline':<20} {'Parallel ({threads}T)':<25} {'Speedup':<15}")
        print("-" * 80)
        print(f"{'Minimum:':<20} {baseline_min_sec:>8.3f}s           {min_sec:>8.3f}s                {baseline_min_sec/min_sec if min_sec else 0:>6.1f}x")
        print(f"{'Average:':<20} {baseline_avg_sec:>8.3f}s           {avg_sec:>8.3f}s                {baseline_avg_sec/avg_sec if avg_sec else 0:>6.1f}x")
        print(f"{'Median (p50):':<20} {'N/A':<20} {p50_sec:>8.3f}s")
        print(f"{'p90:':<20} {'N/A':<20} {p90_sec:>8.3f}s")
        print(f"{'p99:':<20} {'N/A':<20} {p99_sec:>8.3f}s")
        print(f"{'Maximum:':<20} {baseline_max_sec:>8.3f}s           {max_sec:>8.3f}s                {baseline_max_sec/max_sec if max_sec else 0:>6.1f}x")
        
        # Extended baseline comparison
        if 'extended_avg' in baseline_stats:
            ext_avg_sec = baseline_stats['extended_avg'] / 1000.0
            ext_min_sec = baseline_stats['extended_min'] / 1000.0
            ext_max_sec = baseline_stats['extended_max'] / 1000.0
            ext_p50_sec = baseline_stats['extended_p50'] / 1000.0
            ext_p90_sec = baseline_stats['extended_p90'] / 1000.0
            ext_p99_sec = baseline_stats['extended_p99'] / 1000.0
            ext_rps = baseline_stats['extended_rps']
            ext_count = baseline_stats['extended_count']
            
            print(f"\n{'Metric':<20} {'Extended Baseline':<20} {'Parallel ({threads}T)':<25} {'Speedup':<15}")
            print(f"{'':>20} {f'({ext_count} reqs)':<20}")
            print("-" * 80)
            print(f"{'Minimum:':<20} {ext_min_sec:>8.3f}s           {min_sec:>8.3f}s                {ext_min_sec/min_sec if min_sec else 0:>6.1f}x")
            print(f"{'Average:':<20} {ext_avg_sec:>8.3f}s           {avg_sec:>8.3f}s                {ext_avg_sec/avg_sec if avg_sec else 0:>6.1f}x")
            print(f"{'Median (p50):':<20} {ext_p50_sec:>8.3f}s           {p50_sec:>8.3f}s                {ext_p50_sec/p50_sec if p50_sec else 0:>6.1f}x")
            print(f"{'p90:':<20} {ext_p90_sec:>8.3f}s           {p90_sec:>8.3f}s                {ext_p90_sec/p90_sec if p90_sec else 0:>6.1f}x")
            print(f"{'p99:':<20} {ext_p99_sec:>8.3f}s           {p99_sec:>8.3f}s                {ext_p99_sec/p99_sec if p99_sec else 0:>6.1f}x")
            print(f"{'Maximum:':<20} {ext_max_sec:>8.3f}s           {max_sec:>8.3f}s                {ext_max_sec/max_sec if max_sec else 0:>6.1f}x")
            print(f"\n{'Throughput:':<20} {ext_rps:>8.2f} req/s       {actual_rps:>8.2f} req/s           {actual_rps/ext_rps if ext_rps else 0:>6.1f}x")
    else:
        print("\n[PARALLEL TEST LATENCY (seconds)]")
        print("-" * 80)
        print(f"  Minimum:               {min_sec:>8.3f}s")
        print(f"  Average:               {avg_sec:>8.3f}s")
        print(f"  Median (p50):          {p50_sec:>8.3f}s")
        print(f"  p90:                   {p90_sec:>8.3f}s")
        print(f"  p99:                   {p99_sec:>8.3f}s")
        print(f"  Maximum:               {max_sec:>8.3f}s")

    print("\n[STATUS BREAKDOWN]")
    print("-" * 80)
    for status_code in sorted(snap['status_breakdown'].keys()):
        count = snap['status_breakdown'][status_code]
        pct = (count / snap['total'] * 100) if snap['total'] > 0 else 0
        status_symbol = "[OK]" if 200 <= status_code < 400 else "[X]"
        print(f"  {status_symbol} {status_code}:              {count} ({pct:.2f}%)")

    if snap["errors"]:
        print("\n[ERRORS]")
        print("-" * 80)
        for error_type, count in sorted(snap['errors'].items()):
            pct = (count / snap['total'] * 100) if snap['total'] > 0 else 0
            print(f"  {error_type}:  {count} ({pct:.2f}%)")

    print("\n" + "=" * 80)
    print(" " * 24 + "END OF PYSTRESS SUMMARY")
    print("=" * 80)


def main(argv: list[str] | None = None):
    # Check Python version and GIL status first
    check_python_version()
    
    ap = argparse.ArgumentParser(description="pystress: free-threaded Python HTTP load tester")
    ap.add_argument("--config", required=True, help="JSON config path")
    ap.add_argument("--duration", type=int, default=60, help="Test duration seconds (default 60)")
    ap.add_argument("--threads", type=int, default=cpu_count(), help="Number of threads (default: CPU cores)")
    ap.add_argument("--single-request", action="store_true", help="Run single request test and exit")
    ap.add_argument("--baseline-duration", type=int, default=0, help="Extended baseline test duration in seconds (0=skip, default: 0)")
    ap.add_argument("--rps", type=float, default=0.0, help="Target requests per second (0=unlimited, default: 0)")
    ap.add_argument("-o", "--output", type=str, help="Output HTML report file path (default: pystress_report_<timestamp>.html)")
    ap.add_argument("--log", type=str, help="Enable detailed request/response logging to specified file (e.g., pystress_logs.txt)")

    args = ap.parse_args(argv)
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    if "token_acquisition" in cfg:
        token = acquire_token(cfg["token_acquisition"])
        if not token:
            print("ERROR: Failed to acquire token. Aborting test.")
            sys.exit(1)
        if "stress_test" in cfg:
            cfg = cfg["stress_test"]
            if "form" not in cfg:
                cfg["form"] = {}
            cfg["form"]["token"] = token
        else:
            print("ERROR: 'stress_test' section not found in config")
            sys.exit(1)

    print("\n" + "=" * 80)
    print(" " * 20 + "BASELINE: SINGLE REQUEST TEST")
    print("=" * 80)
    print(f"Target URL: {cfg.get('url')}")
    print(f"Method: {cfg.get('method', 'POST')}")
    print(f"Running 5 sequential requests to measure baseline latency...")
    print("-" * 80)

    http = SimpleHttpClient(verify_tls=cfg.get('verify_tls', True))
    headers, data_bytes = build_headers_and_body(cfg)
    method = cfg.get('method', 'POST')
    timeout = float(cfg.get('timeout_ms', 30000)) / 1000.0

    baseline_latencies = []
    for i in range(5):
        try:
            status, ms, error = http.request(method, cfg['url'], headers, data_bytes, timeout=timeout)
            if status > 0:
                baseline_latencies.append(ms)
                print(f"  Request {i+1}: Status={status}, Latency={ms}ms ({ms/1000:.3f}s)")
            else:
                print(f"  Request {i+1}: FAILED after {ms}ms - {error}")
        except Exception as e:
            print(f"  Request {i+1}: FAILED - {e}")

    baseline_stats: dict = {}
    if baseline_latencies:
        avg = sum(baseline_latencies) / len(baseline_latencies)
        min_lat = min(baseline_latencies)
        max_lat = max(baseline_latencies)
        baseline_stats = {'min': min_lat, 'avg': avg, 'max': max_lat, 'quick_count': len(baseline_latencies)}
        print("-" * 80)
        print(f"\n[Quick Baseline Summary - {len(baseline_latencies)} requests]")
        print(f"  Minimum:  {min_lat}ms ({min_lat/1000:.3f}s)")
        print(f"  Average:  {avg:.1f}ms ({avg/1000:.3f}s)")
        print(f"  Maximum:  {max_lat}ms ({max_lat/1000:.3f}s)")
        print("\n" + "=" * 80)

    # Extended baseline test
    if args.baseline_duration > 0:
        print("\n" + "=" * 80)
        print(" " * 15 + f"EXTENDED BASELINE: {args.baseline_duration}s SINGLE-THREADED TEST")
        print("=" * 80)
        print(f"Running continuous requests for {args.baseline_duration}s to measure sustained baseline...")
        print("-" * 80)
        
        extended_latencies = []
        extended_start = time.time()
        extended_count = 0
        extended_ok = 0
        extended_failed = 0
        
        while time.time() - extended_start < args.baseline_duration:
            try:
                status, ms, error = http.request(method, cfg['url'], headers, data_bytes, timeout=timeout)
                extended_count += 1
                
                if status > 0 and not error:
                    extended_latencies.append(ms)
                    extended_ok += 1
                else:
                    extended_failed += 1
                    if extended_failed <= 5:  # Only print first 5 errors
                        print(f"  Request FAILED after {ms}ms - {error}")
                
                # Print progress every 10 requests
                if extended_count % 10 == 0:
                    elapsed = time.time() - extended_start
                    current_rps = extended_count / elapsed if elapsed > 0 else 0
                    if extended_latencies:
                        print(f"  [{elapsed:.1f}s] {extended_count} requests, {current_rps:.2f} req/s, avg latency: {sum(extended_latencies)/len(extended_latencies):.0f}ms")
            except Exception as e:
                extended_count += 1
                extended_failed += 1
                if extended_failed <= 5:  # Only print first 5 errors
                    print(f"  Request FAILED - {e}")
        
        extended_duration = time.time() - extended_start
        
        if extended_latencies:
            ext_avg = sum(extended_latencies) / len(extended_latencies)
            ext_min = min(extended_latencies)
            ext_max = max(extended_latencies)
            ext_rps = extended_count / extended_duration if extended_duration > 0 else 0
            
            # Calculate percentiles
            sorted_latencies = sorted(extended_latencies)
            ext_p50 = sorted_latencies[int(len(sorted_latencies) * 0.50)] if sorted_latencies else 0
            ext_p90 = sorted_latencies[int(len(sorted_latencies) * 0.90)] if sorted_latencies else 0
            ext_p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)] if sorted_latencies else 0
            
            baseline_stats.update({
                'extended_min': ext_min,
                'extended_avg': ext_avg,
                'extended_max': ext_max,
                'extended_p50': ext_p50,
                'extended_p90': ext_p90,
                'extended_p99': ext_p99,
                'extended_count': extended_count,
                'extended_ok': extended_ok,
                'extended_failed': extended_failed,
                'extended_rps': ext_rps,
                'extended_duration': extended_duration
            })
            
            print("-" * 80)
            print(f"\n[Extended Baseline Summary - {extended_count} requests over {extended_duration:.2f}s]")
            print(f"  Throughput:    {ext_rps:.2f} req/s")
            print(f"  Success Rate:  {(extended_ok/extended_count*100):.2f}% ({extended_ok}/{extended_count})")
            print(f"  Minimum:       {ext_min}ms ({ext_min/1000:.3f}s)")
            print(f"  Average:       {ext_avg:.1f}ms ({ext_avg/1000:.3f}s)")
            print(f"  Median (p50):  {ext_p50}ms ({ext_p50/1000:.3f}s)")
            print(f"  p90:           {ext_p90}ms ({ext_p90/1000:.3f}s)")
            print(f"  p99:           {ext_p99}ms ({ext_p99/1000:.3f}s)")
            print(f"  Maximum:       {ext_max}ms ({ext_max/1000:.3f}s)")
            print("\n" + "=" * 80)

    if args.single_request:
        return 0

    print("\n[Starting parallel stress test in 3 seconds...]")
    time.sleep(3)

    # Always single-process: free-threaded Python 3.14t provides thread parallelism
    processes = 1
    threads = max(1, args.threads)
    per_proc_rps = args.rps if args.rps > 0 else 0.0  # Use --rps flag or unlimited

    # Get CPU info
    try:
        import psutil
        physical_cores = psutil.cpu_count(logical=False)
    except:
        physical_cores = cpu_count()
    
    logical_processors = cpu_count()
    gil_disabled = hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled()
    
    print("=" * 80)
    # Check which HTTP backend is being used
    from .http import HAS_URLLIB3
    http_backend = "urllib3 (connection pooling)" if HAS_URLLIB3 else "urllib.request (no pooling)"
    
    print("PYSTRESS CONFIGURATION")
    print("=" * 80)
    print(f"Physical CPU Cores:      {physical_cores}")
    print(f"Logical Processors:      {logical_processors}{f' ({logical_processors//physical_cores}x hyperthreading)' if logical_processors > physical_cores else ''}")
    print(f"GIL Status:              {'[OK] DISABLED (True parallelism)' if gil_disabled else '[!] ENABLED (Sequential execution)'}")
    print(f"Worker Threads:          {threads} {'threads will execute in parallel' if gil_disabled else 'threads (only 1 executes at a time)'}")
    print(f"HTTP Backend:            {http_backend}")
    print("-" * 80)
    print(f"Test URL:                {cfg.get('url')}")
    print(f"Method:                  {cfg.get('method', 'POST')}")
    print(f"Duration:                {args.duration}s")
    if per_proc_rps > 0:
        print(f"Rate Limit:              {per_proc_rps:.1f} req/s (throttled)")
    else:
        print(f"Rate Limit:              Unlimited (max speed)")
    print(f"Timeout:                 {cfg.get('timeout_ms', 30000)}ms")
    print(f"Retries:                 {cfg.get('retries', 0)}")
    print(f"Verify TLS:              {cfg.get('verify_tls', True)}")
    print(f"Basic Auth:              {'Yes' if cfg.get('basic_auth') else 'No'}")
    if cfg.get('form'):
        print(f"Form data fields:        {list(cfg['form'].keys())}")
    print("=" * 80)
    print(f"Starting test at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    print("=" * 80, flush=True)

    # Initialize logger if requested
    logger = RequestLogger(args.log) if args.log else None
    if logger and logger.enabled:
        print(f"[OK] Detailed logging enabled: {args.log}\n")
    
    ctx = get_context("spawn")
    q = ctx.Queue()
    workers: list[threading.Thread] = []
    # Single background thread running the worker function; still reports via queue
    t = threading.Thread(target=worker_process, args=(0, cfg, args.duration, threads, per_proc_rps, q, logger), daemon=True)
    t.start()
    workers.append(t)

    merged = Metrics()
    finished = 0
    start_wall = time.time()
    last_print = 0
    proc_snapshots: dict[int, dict] = {}

    while finished < processes:
        try:
            msg_type, proc_idx, data = q.get(timeout=0.5)
            if msg_type == "done":
                merged.total += data.get('total', 0)
                merged.ok += data.get('ok', 0)
                for status, count in data.get('status_breakdown', {}).items():
                    merged.statuses[int(status)] += count
                for error, count in data.get('errors', {}).items():
                    merged.errors[error] += count

                total_reqs = data.get('total', 0)
                if total_reqs > 0:
                    min_ms = data.get('min_ms', 0)
                    avg_ms = data.get('avg_ms', 0)
                    max_ms = data.get('max_ms', 0)
                    p50_ms = data.get('p50_ms', 0)
                    p90_ms = data.get('p90_ms', 0)
                    p99_ms = data.get('p99_ms', 0)
                    for idx in range(total_reqs):
                        if idx == 0:
                            merged.latencies.append(min_ms)
                        elif idx == total_reqs - 1:
                            merged.latencies.append(max_ms)
                        elif idx == int(total_reqs * 0.5):
                            merged.latencies.append(p50_ms)
                        elif idx == int(total_reqs * 0.9):
                            merged.latencies.append(p90_ms)
                        elif idx == int(total_reqs * 0.99):
                            merged.latencies.append(p99_ms)
                        else:
                            merged.latencies.append(avg_ms)

                finished += 1
            elif msg_type == "progress":
                proc_snapshots[proc_idx] = data
        except Exception:
            elapsed = int(time.time() - start_wall)
            if elapsed > 0 and elapsed != last_print and elapsed % 10 == 0:
                last_print = elapsed
                total_reqs = sum(s['total'] for s in proc_snapshots.values())
                total_ok = sum(s['ok'] for s in proc_snapshots.values())
                print(f"[{elapsed}s] Progress: {total_reqs:,} requests, {total_ok:,} successful", flush=True)

    for t in workers:
        t.join()
    
    # Close logger if enabled
    if logger and logger.enabled:
        logger.close()
        print(f"\n[OK] Detailed log saved: {args.log}")

    snap = merged.snapshot()
    print_summary(args, merged, threads, baseline_stats, start_wall)
    
    # Generate and save HTML report
    html_content, default_filename = generate_html_report(
        config_path=args.config,
        cfg=cfg,
        args=args,
        snap=snap,
        baseline_stats=baseline_stats,
        threads=threads,
        total_elapsed=max(1, time.time() - start_wall),
        start_time=start_wall,
    )
    
    # Use user-specified output path or default
    output_path = args.output if args.output else default_filename
    
    # Create parent directory if it doesn't exist
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n[OK] HTML report saved: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



