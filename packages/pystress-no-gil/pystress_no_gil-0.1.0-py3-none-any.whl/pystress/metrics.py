from __future__ import annotations

import math
import random
import threading
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Metrics:
    """
    Thread-safe metrics collector with reservoir sampling for percentiles.
    
    Uses reservoir sampling to keep memory bounded while maintaining
    accurate percentile estimates even for very long tests.
    """
    total: int = 0
    ok: int = 0
    statuses: dict = field(default_factory=lambda: defaultdict(int))
    errors: dict = field(default_factory=lambda: defaultdict(int))
    latencies: list[int] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    
    # Reservoir sampling parameters
    max_reservoir_size: int = 100_000  # Keep up to 100k samples for percentiles
    reservoir_count: int = 0  # Total samples processed
    
    def add(self, status: int, ms: int, error: str | None = None):
        """Add a request result with reservoir sampling for latencies."""
        with self.lock:
            self.total += 1
            self.statuses[status] += 1
            if 200 <= status < 400 and not error:
                self.ok += 1
            if error:
                self.errors[error] += 1
            
            # Reservoir sampling: keep up to max_reservoir_size latencies
            # This gives accurate percentiles while bounding memory
            if len(self.latencies) < self.max_reservoir_size:
                self.latencies.append(ms)
            else:
                # Randomly replace an existing sample
                # Probability of keeping this sample = reservoir_size / total_samples
                self.reservoir_count += 1
                idx = random.randint(0, self.reservoir_count + self.max_reservoir_size - 1)
                if idx < self.max_reservoir_size:
                    self.latencies[idx] = ms

    def merge(self, other: "Metrics"):
        """Merge another Metrics object into this one."""
        with self.lock:
            self.total += other.total
            self.ok += other.ok
            for k, v in other.statuses.items():
                self.statuses[k] += v
            for k, v in other.errors.items():
                self.errors[k] += v
            
            # Merge latencies with reservoir sampling
            for lat in other.latencies:
                if len(self.latencies) < self.max_reservoir_size:
                    self.latencies.append(lat)
                else:
                    self.reservoir_count += 1
                    idx = random.randint(0, self.reservoir_count + self.max_reservoir_size - 1)
                    if idx < self.max_reservoir_size:
                        self.latencies[idx] = lat

    def snapshot(self) -> dict:
        """
        Get current metrics snapshot with accurate percentiles.
        
        Percentiles are calculated from actual latency samples (not interpolated).
        """
        with self.lock:
            lats = sorted(self.latencies)

            def pct(p: float) -> int:
                """Calculate percentile using nearest-rank method."""
                if not lats:
                    return 0
                # Use ceiling for percentile index (nearest-rank method)
                # This is the standard approach used by most monitoring tools
                idx = int(math.ceil(len(lats) * p)) - 1
                idx = max(0, min(len(lats) - 1, idx))
                return int(lats[idx])

            return {
                "total": self.total,
                "ok": self.ok,
                "status_breakdown": dict(sorted(self.statuses.items())),
                "errors": dict(sorted(self.errors.items())),
                "p50_ms": pct(0.50),
                "p90_ms": pct(0.90),
                "p99_ms": pct(0.99),
                "p95_ms": pct(0.95),  # Added p95
                "avg_ms": int(sum(lats) / len(lats)) if lats else 0,
                "min_ms": int(lats[0]) if lats else 0,
                "max_ms": int(lats[-1]) if lats else 0,
                "sample_count": len(lats),  # How many samples we're using
            }
