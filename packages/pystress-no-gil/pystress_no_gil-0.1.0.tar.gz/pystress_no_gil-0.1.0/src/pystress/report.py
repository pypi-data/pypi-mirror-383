from __future__ import annotations

import platform
import sys
import time
from multiprocessing import cpu_count
from pathlib import Path


def generate_html_report(
    config_path: str,
    cfg: dict,
    args,
    snap: dict,
    baseline_stats: dict,
    threads: int,
    total_elapsed: float,
    start_time: float,
) -> str:
    """Generate a styled HTML report with all test details."""
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    report_filename = f"pystress_report_{time.strftime('%Y%m%d_%H%M%S', time.localtime(start_time))}.html"
    
    # Calculate metrics
    total_requests = snap['total']
    passed_requests = snap['ok']
    failed_requests = total_requests - passed_requests
    pass_rate = (passed_requests / total_requests * 100) if total_requests > 0 else 0
    fail_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
    actual_rps = total_requests / total_elapsed if total_elapsed > 0 else 0
    
    min_sec = snap['min_ms'] / 1000.0
    max_sec = snap['max_ms'] / 1000.0
    avg_sec = snap['avg_ms'] / 1000.0
    p50_sec = snap['p50_ms'] / 1000.0
    p90_sec = snap['p90_ms'] / 1000.0
    p99_sec = snap['p99_ms'] / 1000.0
    
    # Hardware info
    import psutil
    physical_cores = psutil.cpu_count(logical=False) if 'psutil' in sys.modules or True else None
    logical_processors = cpu_count()
    
    try:
        import psutil
        physical_cores = psutil.cpu_count(logical=False)
    except:
        # Fallback if psutil not available
        physical_cores = logical_processors
    
    hw_info = {
        'os': f"{platform.system()} {platform.release()}",
        'arch': platform.machine(),
        'python': f"{sys.version.split()[0]}",
        'physical_cores': physical_cores,
        'logical_processors': logical_processors,
        'gil_disabled': not sys._is_gil_enabled() if hasattr(sys, '_is_gil_enabled') else False,
    }
    
    # Build status breakdown HTML
    status_rows = []
    for status_code in sorted(snap['status_breakdown'].keys()):
        count = snap['status_breakdown'][status_code]
        pct = (count / total_requests * 100) if total_requests > 0 else 0
        if 200 <= status_code < 400:
            badge_class = "badge-success-custom"
            icon = "bi-check-circle-fill"
            status_text = f"{status_code} OK" if status_code == 200 else str(status_code)
        else:
            badge_class = "badge-error-custom"
            icon = "bi-x-circle-fill"
            status_text = str(status_code)
        status_rows.append(
            f'<tr><td><span class="badge-custom {badge_class}"><i class="bi {icon}"></i> {status_text}</span></td><td><strong>{count:,}</strong></td><td class="{'status-success' if 200 <= status_code < 400 else 'status-error'}">{pct:.2f}%</td></tr>'
        )
    
    # Build error breakdown HTML
    error_rows = []
    if snap.get('errors'):
        for error_type, count in sorted(snap['errors'].items()):
            pct = (count / total_requests * 100) if total_requests > 0 else 0
            error_rows.append(
                f'<tr><td>{error_type}</td><td>{count:,}</td><td>{pct:.2f}%</td></tr>'
            )
    
    # Baseline comparison
    baseline_html = ""
    if baseline_stats:
        baseline_avg_sec = baseline_stats['avg'] / 1000.0
        baseline_min_sec = baseline_stats['min'] / 1000.0
        baseline_max_sec = baseline_stats['max'] / 1000.0
        slowdown_min = min_sec / baseline_min_sec if baseline_min_sec else 0
        slowdown_avg = avg_sec / baseline_avg_sec if baseline_avg_sec else 0
        slowdown_max = max_sec / baseline_max_sec if baseline_max_sec else 0
        
        # Quick baseline table
        quick_count = baseline_stats.get('quick_count', 5)
        baseline_html = f"""
                <div class="mb-5">
                    <h2 class="section-title"><i class="bi bi-graph-up"></i> Baseline Comparison</h2>
                    <h5 class="text-muted mb-3"><i class="bi bi-clock"></i> Quick Baseline ({quick_count} sequential requests)</h5>
                    <div class="table-wrapper">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Baseline (Single)</th>
                                    <th>Parallel ({threads} threads)</th>
                                    <th>Speedup</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>Minimum</strong></td>
                                    <td>{baseline_min_sec:.3f}s</td>
                                    <td>{min_sec:.3f}s</td>
                                    <td><span class="badge-custom {'badge-success-custom' if baseline_min_sec/min_sec >= 1.0 else 'badge-danger-custom' if baseline_min_sec/min_sec < 0.5 else 'badge-warning-custom'}">{baseline_min_sec/min_sec if min_sec else 0:.1f}x {'⚡ Speedup' if baseline_min_sec/min_sec >= 1.0 else '🐌 Slowdown'}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Average</strong></td>
                                    <td>{baseline_avg_sec:.3f}s</td>
                                    <td>{avg_sec:.3f}s</td>
                                    <td><span class="badge-custom {'badge-success-custom' if baseline_avg_sec/avg_sec >= 1.0 else 'badge-danger-custom' if baseline_avg_sec/avg_sec < 0.5 else 'badge-warning-custom'}">{baseline_avg_sec/avg_sec if avg_sec else 0:.1f}x {'⚡ Speedup' if baseline_avg_sec/avg_sec >= 1.0 else '🐌 Slowdown'}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Maximum</strong></td>
                                    <td>{baseline_max_sec:.3f}s</td>
                                    <td>{max_sec:.3f}s</td>
                                    <td><span class="badge-custom {'badge-success-custom' if baseline_max_sec/max_sec >= 1.0 else 'badge-danger-custom' if baseline_max_sec/max_sec < 0.5 else 'badge-warning-custom'}">{baseline_max_sec/max_sec if max_sec else 0:.1f}x {'⚡ Speedup' if baseline_max_sec/max_sec >= 1.0 else '🐌 Slowdown'}</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
        """
        
        # Extended baseline table if available
        if 'extended_avg' in baseline_stats:
            ext_avg_sec = baseline_stats['extended_avg'] / 1000.0
            ext_min_sec = baseline_stats['extended_min'] / 1000.0
            ext_max_sec = baseline_stats['extended_max'] / 1000.0
            ext_p50_sec = baseline_stats['extended_p50'] / 1000.0
            ext_p90_sec = baseline_stats['extended_p90'] / 1000.0
            ext_p99_sec = baseline_stats['extended_p99'] / 1000.0
            ext_rps = baseline_stats['extended_rps']
            ext_count = baseline_stats['extended_count']
            ext_duration = baseline_stats['extended_duration']
            
            speedup_min = ext_min_sec / min_sec if min_sec else 0
            speedup_avg = ext_avg_sec / avg_sec if avg_sec else 0
            speedup_p50 = ext_p50_sec / p50_sec if p50_sec else 0
            speedup_p90 = ext_p90_sec / p90_sec if p90_sec else 0
            speedup_p99 = ext_p99_sec / p99_sec if p99_sec else 0
            speedup_max = ext_max_sec / max_sec if max_sec else 0
            speedup_rps = actual_rps / ext_rps if ext_rps else 0
            
            baseline_html += f"""
                    <h5 class="text-muted mb-3 mt-4"><i class="bi bi-hourglass-split"></i> Extended Baseline ({ext_count} requests over {ext_duration:.1f}s)</h5>
                    <div class="table-wrapper">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Extended Baseline</th>
                                    <th>Parallel ({threads} threads)</th>
                                    <th>Speedup</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>Throughput</strong></td>
                                    <td>{ext_rps:.2f} req/s</td>
                                    <td>{actual_rps:.2f} req/s</td>
                                    <td><span class="badge-custom {'badge-success-custom' if speedup_rps >= 1.0 else 'badge-danger-custom' if speedup_rps < 0.5 else 'badge-warning-custom'}"><i class="bi bi-lightning-fill"></i> {speedup_rps:.1f}x {'⚡' if speedup_rps >= 1.0 else '🐌'}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Minimum</strong></td>
                                    <td>{ext_min_sec:.3f}s</td>
                                    <td>{min_sec:.3f}s</td>
                                    <td><span class="badge-custom {'badge-success-custom' if speedup_min >= 1.0 else 'badge-danger-custom' if speedup_min < 0.5 else 'badge-warning-custom'}">{speedup_min:.1f}x {'⚡' if speedup_min >= 1.0 else '🐌'}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Average</strong></td>
                                    <td>{ext_avg_sec:.3f}s</td>
                                    <td>{avg_sec:.3f}s</td>
                                    <td><span class="badge-custom {'badge-success-custom' if speedup_avg >= 1.0 else 'badge-danger-custom' if speedup_avg < 0.5 else 'badge-warning-custom'}">{speedup_avg:.1f}x {'⚡' if speedup_avg >= 1.0 else '🐌'}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Median (p50)</strong></td>
                                    <td>{ext_p50_sec:.3f}s</td>
                                    <td>{p50_sec:.3f}s</td>
                                    <td><span class="badge-custom {'badge-success-custom' if speedup_p50 >= 1.0 else 'badge-danger-custom' if speedup_p50 < 0.5 else 'badge-warning-custom'}">{speedup_p50:.1f}x {'⚡' if speedup_p50 >= 1.0 else '🐌'}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>p90</strong></td>
                                    <td>{ext_p90_sec:.3f}s</td>
                                    <td>{p90_sec:.3f}s</td>
                                    <td><span class="badge-custom {'badge-success-custom' if speedup_p90 >= 1.0 else 'badge-danger-custom' if speedup_p90 < 0.5 else 'badge-warning-custom'}">{speedup_p90:.1f}x {'⚡' if speedup_p90 >= 1.0 else '🐌'}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>p99</strong></td>
                                    <td>{ext_p99_sec:.3f}s</td>
                                    <td>{p99_sec:.3f}s</td>
                                    <td><span class="badge-custom {'badge-success-custom' if speedup_p99 >= 1.0 else 'badge-danger-custom' if speedup_p99 < 0.5 else 'badge-warning-custom'}">{speedup_p99:.1f}x {'⚡' if speedup_p99 >= 1.0 else '🐌'}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Maximum</strong></td>
                                    <td>{ext_max_sec:.3f}s</td>
                                    <td>{max_sec:.3f}s</td>
                                    <td><span class="badge-custom {'badge-success-custom' if speedup_max >= 1.0 else 'badge-danger-custom' if speedup_max < 0.5 else 'badge-warning-custom'}">{speedup_max:.1f}x {'⚡' if speedup_max >= 1.0 else '🐌'}</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
        """
        else:
            baseline_html += "</div>"
    
    # Prepare GIL status badge
    gil_badge_color = "success-custom" if hw_info['gil_disabled'] else "warning-custom"
    gil_status_text = "DISABLED" if hw_info['gil_disabled'] else "ENABLED"
    gil_icon = "bi-check-circle-fill" if hw_info['gil_disabled'] else "bi-exclamation-triangle-fill"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pystress Report - {timestamp}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        :root {{
            --primary-green: #10b981;
            --light-green: #d1fae5;
            --lighter-green: #f0fdf4;
            --dark-gray: #1f2937;
            --medium-gray: #6b7280;
            --light-gray: #f9fafb;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f3f4f6;
            padding: 2rem 0;
        }}
        
        .report-container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .report-header {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 3rem 2rem;
        }}
        
        .report-header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .report-header .subtitle {{
            font-size: 1.1rem;
            opacity: 0.95;
        }}
        
        .report-content {{
            padding: 2rem;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--dark-gray);
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--light-green);
        }}
        
        .stat-card {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.5rem;
            height: 100%;
            transition: all 0.2s ease;
        }}
        
        .stat-card:hover {{
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
            border-color: var(--light-green);
        }}
        
        .stat-card .icon {{
            width: 48px;
            height: 48px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }}
        
        .stat-card .icon.green {{
            background: var(--lighter-green);
            color: var(--primary-green);
        }}
        
        .stat-card .icon.gray {{
            background: var(--light-gray);
            color: var(--medium-gray);
        }}
        
        .stat-card .icon.orange {{
            background: #fef3c7;
            color: #d97706;
        }}
        
        .stat-card .label {{
            font-size: 0.875rem;
            color: var(--medium-gray);
            font-weight: 500;
            margin-bottom: 0.5rem;
        }}
        
        .stat-card .value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--dark-gray);
        }}
        
        .stat-card .unit {{
            font-size: 0.875rem;
            color: var(--medium-gray);
            font-weight: 500;
        }}
        
        .hero-card {{
            background: linear-gradient(135deg, var(--lighter-green) 0%, white 100%);
            border: 2px solid var(--light-green);
            border-radius: 12px;
            padding: 2.5rem;
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .hero-card .label {{
            font-size: 0.875rem;
            color: var(--medium-gray);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 1rem;
        }}
        
        .hero-card .value {{
            font-size: 4rem;
            font-weight: 800;
            color: var(--primary-green);
            line-height: 1;
            margin-bottom: 1rem;
        }}
        
        .hero-card .subtitle {{
            font-size: 1.125rem;
            color: var(--medium-gray);
            font-weight: 500;
        }}
        
        .endpoint-card {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border-radius: 12px;
            padding: 2rem;
            color: white;
            margin-bottom: 2rem;
        }}
        
        .endpoint-card .label {{
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1rem;
            opacity: 0.9;
        }}
        
        .endpoint-card .url {{
            font-size: 1.5rem;
            font-weight: 600;
            word-break: break-all;
            background: rgba(255, 255, 255, 0.15);
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }}
        
        .endpoint-card .method {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.25);
            padding: 0.5rem 1.5rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 1rem;
        }}
        
        .table-wrapper {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e5e7eb;
        }}
        
        .table {{
            margin-bottom: 0;
        }}
        
        .table thead {{
            background: var(--lighter-green);
        }}
        
        .table thead th {{
            color: var(--primary-green);
            font-weight: 700;
            border-bottom: 2px solid var(--light-green);
            padding: 1rem;
        }}
        
        .table tbody td {{
            padding: 1rem;
            color: var(--dark-gray);
            vertical-align: middle;
        }}
        
        .table tbody tr:hover {{
            background: var(--light-gray);
        }}
        
        .badge-custom {{
            padding: 0.375rem 0.75rem;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        
        .badge-success-custom {{
            background: var(--light-green);
            color: var(--primary-green);
        }}
        
        .badge-warning-custom {{
            background: #fef3c7;
            color: #d97706;
        }}
        
        .badge-error-custom {{
            background: #fee2e2;
            color: #dc2626;
        }}
        
        .status-success {{
            color: var(--primary-green);
            font-weight: 700;
        }}
        
        .status-error {{
            color: #dc2626;
            font-weight: 700;
        }}
        
        .badge-danger-custom {{
            background: #dc2626;
            color: white;
            font-weight: 700;
        }}
        
        .footer {{
            background: var(--light-gray);
            padding: 2rem;
            text-align: center;
            color: var(--medium-gray);
            border-top: 1px solid #e5e7eb;
        }}
        
        .footer p {{
            margin-bottom: 0.5rem;
        }}
        
        .quick-stats {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }}
        
        .quick-stats .row > div {{
            text-align: center;
            padding: 1rem;
        }}
        
        .quick-stats .stat-number {{
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--primary-green);
            margin-bottom: 0.25rem;
        }}
        
        .quick-stats .stat-label {{
            font-size: 0.875rem;
            color: var(--medium-gray);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .quick-stats .divider {{
            width: 1px;
            background: #e5e7eb;
            height: 60px;
            margin: auto;
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="report-header">
            <div class="container-fluid">
                <h1><i class="bi bi-lightning-charge-fill"></i> pystress Load Test Report</h1>
                <div class="subtitle">Generated on {timestamp}</div>
            </div>
        </div>
        
        <div class="report-content">
            <div class="container-fluid">
                <div class="endpoint-card">
                    <div class="label"><i class="bi bi-bullseye"></i> TARGET ENDPOINT</div>
                    <div class="url">{cfg.get('url', 'N/A')}</div>
                    <div class="method">{cfg.get('method', 'POST')}</div>
                </div>
                
                <div class="hero-card">
                    <div class="label"><i class="bi bi-bar-chart-fill"></i> Total Requests Processed</div>
                    <div class="value">{total_requests:,}</div>
                    <div class="subtitle"><i class="bi bi-speedometer2"></i> {actual_rps:.2f} requests/second • <i class="bi bi-clock"></i> {total_elapsed:.2f}s duration</div>
                </div>
                
                <div class="quick-stats">
                    <div class="row">
                        <div class="col">
                            <div class="stat-number {'status-success' if pass_rate >= 95 else 'status-error' if pass_rate < 80 else ''}">{pass_rate:.0f}%</div>
                            <div class="stat-label"><i class="bi {'bi-check-circle' if pass_rate >= 95 else 'bi-exclamation-triangle-fill' if pass_rate < 80 else 'bi-dash-circle'}"></i> Pass Rate</div>
                        </div>
                        <div class="col d-none d-md-flex align-items-center">
                            <div class="divider"></div>
                        </div>
                        <div class="col">
                            <div class="stat-number status-success">{passed_requests:,}</div>
                            <div class="stat-label"><i class="bi bi-check-square"></i> Passed</div>
                        </div>
                        <div class="col d-none d-md-flex align-items-center">
                            <div class="divider"></div>
                        </div>
                        <div class="col">
                            <div class="stat-number {'status-error' if failed_requests > 0 else ''}">{failed_requests:,}</div>
                            <div class="stat-label"><i class="bi bi-x-square"></i> Failed</div>
                        </div>
                        <div class="col d-none d-md-flex align-items-center">
                            <div class="divider"></div>
                        </div>
                        <div class="col">
                            <div class="stat-number">{actual_rps:.2f}</div>
                            <div class="stat-label"><i class="bi bi-speedometer"></i> Actual RPS</div>
                        </div>
                    </div>
                </div>
                
                <div class="mb-5">
                    <h2 class="section-title"><i class="bi bi-gear-fill"></i> Test Configuration</h2>
                    <div class="row g-3">
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-hourglass-split"></i>
                                </div>
                                <div class="label">Duration</div>
                                <div class="value">{args.duration} <span class="unit">sec</span></div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-bezier2"></i>
                                </div>
                                <div class="label">Threads</div>
                                <div class="value">{threads}</div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-alarm"></i>
                                </div>
                                <div class="label">Timeout</div>
                                <div class="value">{cfg.get('timeout_ms', 30000)} <span class="unit">ms</span></div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-arrow-repeat"></i>
                                </div>
                                <div class="label">Retries</div>
                                <div class="value">{cfg.get('retries', 0)}</div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon green">
                                    <i class="bi bi-shield-check"></i>
                                </div>
                                <div class="label">TLS Verification</div>
                                <div class="value" style="font-size: 1.25rem;">{'Enabled' if cfg.get('verify_tls', True) else 'Disabled'}</div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon green">
                                    <i class="bi bi-lightning-fill"></i>
                                </div>
                                <div class="label">Mode</div>
                                <div class="value" style="font-size: 1rem;">Max Speed</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mb-5">
                    <h2 class="section-title"><i class="bi bi-pc-display"></i> Hardware & Environment</h2>
                    <div class="row g-3">
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-windows"></i>
                                </div>
                                <div class="label">Operating System</div>
                                <div class="value" style="font-size: 1.25rem;">{hw_info['os']}</div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-cpu"></i>
                                </div>
                                <div class="label">Architecture</div>
                                <div class="value" style="font-size: 1.25rem;">{hw_info['arch']}</div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-code-slash"></i>
                                </div>
                                <div class="label">Python Version</div>
                                <div class="value">{hw_info['python']}</div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-cpu-fill"></i>
                                </div>
                                <div class="label">Physical Cores</div>
                                <div class="value">{hw_info['physical_cores']}</div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-diagram-3"></i>
                                </div>
                                <div class="label">Logical Processors</div>
                                <div class="value">{hw_info['logical_processors']}</div>
                                <div style="font-size: 0.75rem; color: #666; margin-top: 0.25rem;">
                                    {f"{hw_info['logical_processors']//hw_info['physical_cores']}x HT" if hw_info['logical_processors'] > hw_info['physical_cores'] else 'No HT'}
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon {'green' if hw_info['gil_disabled'] else 'orange'}">
                                    <i class="bi {gil_icon}"></i>
                                </div>
                                <div class="label">GIL Status</div>
                                <div class="value" style="font-size: 1rem;">{gil_status_text}</div>
                                <div style="font-size: 0.75rem; color: #666; margin-top: 0.25rem;">
                                    {f'{hw_info["logical_processors"]} parallel' if hw_info['gil_disabled'] else 'Sequential'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mb-5">
                    <h2 class="section-title"><i class="bi bi-clock-history"></i> Latency Statistics</h2>
                    <div class="row g-3">
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon green">
                                    <i class="bi bi-arrow-down-circle"></i>
                                </div>
                                <div class="label">Minimum</div>
                                <div class="value">{min_sec:.3f} <span class="unit">s</span></div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon green">
                                    <i class="bi bi-graph-down"></i>
                                </div>
                                <div class="label">Average</div>
                                <div class="value">{avg_sec:.3f} <span class="unit">s</span></div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-dash-circle"></i>
                                </div>
                                <div class="label">Median (p50)</div>
                                <div class="value">{p50_sec:.3f} <span class="unit">s</span></div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-bar-chart"></i>
                                </div>
                                <div class="label">p90</div>
                                <div class="value">{p90_sec:.3f} <span class="unit">s</span></div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-bar-chart-fill"></i>
                                </div>
                                <div class="label">p99</div>
                                <div class="value">{p99_sec:.3f} <span class="unit">s</span></div>
                            </div>
                        </div>
                        <div class="col-md-4 col-lg-2">
                            <div class="stat-card">
                                <div class="icon gray">
                                    <i class="bi bi-arrow-up-circle"></i>
                                </div>
                                <div class="label">Maximum</div>
                                <div class="value">{max_sec:.3f} <span class="unit">s</span></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                {baseline_html}
                
                <div class="mb-4">
                    <h2 class="section-title"><i class="bi bi-clipboard-data"></i> HTTP Status Breakdown</h2>
                    <div class="table-wrapper">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Status Code</th>
                                    <th>Count</th>
                                    <th>Percentage</th>
                                </tr>
                            </thead>
                            <tbody>
                                {"".join(status_rows)}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                {f'''<div class="mb-4">
                    <h2 class="section-title"><i class="bi bi-exclamation-triangle"></i> Error Breakdown</h2>
                    <div class="table-wrapper">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Error Type</th>
                                    <th>Count</th>
                                    <th>Percentage</th>
                                </tr>
                            </thead>
                            <tbody>
                                {"".join(error_rows)}
                            </tbody>
                        </table>
                    </div>
                </div>''' if error_rows else ''}
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Generated by pystress</strong> • High-performance, free-threaded HTTP load tester</p>
            <p>Report: {report_filename}</p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    return html, report_filename

