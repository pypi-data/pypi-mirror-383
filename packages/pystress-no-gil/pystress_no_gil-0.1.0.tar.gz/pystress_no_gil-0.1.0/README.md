# PyStress

**High-performance HTTP load testing with Python 3.14's free-threading (no-GIL)**

By [Hammad Abbasi](https://hammadabbasi.com)

---

## ⚡ Quick Start

```bash
# 1. Download Python 3.14t (free-threaded)
# Windows: https://www.python.org/ftp/python/3.14.0/python-3.14.0t-amd64.zip
# Extract to C:\Python314t

# 2. Install PyStress
C:\Python314t\python.exe -m pip install -e .

# 3. Run
C:\Python314t\python.exe -m pystress --config test.json --threads 24
```

---

## 🎯 Why PyStress?

- **True Parallelism**: Python 3.14t's GIL-free execution → all CPU cores working simultaneously
- **Zero Dependencies**: Only `psutil` for CPU detection
- **Beautiful Reports**: Bootstrap 5 HTML reports with green design
- **Production Ready**: OAuth2, retries, detailed logging, metrics

**Performance:** With 16 cores (24 threads with hyperthreading), expect **~24x throughput** vs single-threaded.

---

## 📋 Requirements

**Required:**
- Python 3.14t (free-threaded build) - **GIL must be disabled**

**Check your Python:**
```bash
python -c "import sys; print(sys._is_gil_enabled())"
# Must print: False
```

**If True:** You have standard Python 3.14, not the free-threaded version.

---

## 📦 Installation

### Windows

```powershell
# Download free-threaded Python 3.14t
Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.14.0/python-3.14.0t-amd64.zip -OutFile python314t.zip

# Extract
Expand-Archive python314t.zip -DestinationPath C:\Python314t

# Install PyStress
C:\Python314t\python.exe -m pip install -e .
```

### Linux

```bash
# Build from source
git clone https://github.com/python/cpython.git
cd cpython
git checkout v3.14.0
./configure --disable-gil --prefix=/opt/python314t
make -j$(nproc)
sudo make install

# Install PyStress
/opt/python314t/bin/python3 -m pip install -e .
```

---

## 🚀 Usage

### Basic Command

```bash
python3.14t -m pystress --config CONFIG [OPTIONS]
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--config` | *required* | JSON config file |
| `--threads` | CPU count | Worker threads (use logical processor count) |
| `--duration` | 60 | Test duration (seconds) |
| `--baseline-duration` | 0 | Extended baseline test (seconds, 0=skip) |
| `--output` | auto | HTML report path |
| `--log` | none | Detailed request log file |

### Examples

```bash
# Basic test
python3.14t -m pystress --config api.json

# Max parallelism (24 threads on 16-core CPU with HT)
python3.14t -m pystress --config api.json --threads 24 --duration 120

# With extended baseline (30s) for accurate comparison
python3.14t -m pystress --config api.json \
    --threads 24 \
    --baseline-duration 30 \
    --duration 60

# With output and logging
python3.14t -m pystress --config api.json \
    --threads 24 \
    --output reports/load_test.html \
    --log logs/requests.log
```

---

## 📝 Configuration

### Basic Config

```json
{
  "url": "https://api.example.com/endpoint",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "json": {
    "key": "value"
  }
}
```

### With OAuth2

```json
{
  "token_acquisition": {
    "url": "https://auth.example.com/token",
    "method": "POST",
    "form": {
      "grant_type": "client_credentials",
      "client_id": "your-client-id",
      "client_secret": "your-secret"
    }
  },
  "stress_test": {
    "url": "https://api.example.com/protected",
    "method": "POST",
    "json": {"data": "value"}
  }
}
```

### All Options

```json
{
  "url": "https://api.example.com/endpoint",
  "method": "POST",
  "timeout_ms": 30000,
  "retries": 3,
  "backoff_ms": 200,
  "backoff_max_ms": 2000,
  "jitter_ms": 100,
  "retry_on_statuses": [429, 503],
  "verify_tls": true,
  "headers": {},
  "json": {},
  "form": {},
  "basic_auth": {
    "username": "user",
    "password": "pass"
  }
}
```

---

## 📊 Baseline Testing

PyStress runs baseline tests before parallel testing to measure single-threaded performance:

### Quick Baseline (Always Runs)
- **5 sequential requests**
- Fast measurement for basic comparison
- May include cold-start overhead

### Extended Baseline (Optional)
- **Continuous requests for N seconds** (use `--baseline-duration`)
- More accurate sustained performance
- Captures warm-up effects and patterns
- Shows single-threaded throughput

**When to use extended baseline:**
- Production-like scenarios
- Comparing cache warm vs cold
- Accurate parallel speedup metrics
- Server performance tuning

**Example:**
```bash
# 30s baseline + 60s parallel test
python3.14t -m pystress --config api.json \
    --baseline-duration 30 \
    --duration 60 \
    --threads 24
```

**Output includes:**
- **Quick**: 5 requests comparison
- **Extended**: Full metrics (min, avg, p50, p90, p99, max, RPS)
- **Speedup calculations** showing parallel improvement

---

## 📊 Output

### Console

```
PYSTRESS CONFIGURATION
Physical CPU Cores:      16
Logical Processors:      24 (1.5x hyperthreading)
GIL Status:              [OK] DISABLED (True parallelism)
Worker Threads:          24 threads will execute in parallel

PYSTRESS SUMMARY
Duration:                60.03s
Total Requests:          1,440
Actual RPS:              24.0 req/s
Pass Rate:               100%
```

### HTML Report

- **Bootstrap 5** design with green theme
- **Prominent endpoint** display
- **Hardware details**: physical cores + logical processors
- **GIL status** with color coding
- **Latency statistics**: min, avg, p50, p90, p99, max
- **Baseline comparison**: single vs parallel performance

---

## 🔧 Python 3.14 Free-Threading

### What It Is

Python 3.14t removes the Global Interpreter Lock (GIL), allowing **true parallel execution** on multiple CPU cores.

**Traditional Python:**
```
Only 1 thread executes at a time
23/24 cores sit IDLE
CPU usage: ~4%
```

**Python 3.14t (no-GIL):**
```
All 24 threads execute simultaneously
All cores fully utilized
CPU usage: ~100%
Performance: ~24x improvement
```

### Your CPU: 16 Cores, 24 Threads

- **Physical Cores:** 16 hardware execution units
- **Logical Processors:** 24 (with hyperthreading)
- **Optimal Threads:** 24 for PyStress (use all logical processors)

**Expected Performance:**
- Single-threaded: 1x baseline
- 16 threads: ~15-16x faster
- 24 threads: ~20-24x faster (best)

---

## 💼 Real-World Examples

### CI/CD Pipeline

```bash
#!/bin/bash
TEST_ID=$(date +%Y%m%d_%H%M%S)
python3.14t -m pystress --config api_test.json \
    --threads 24 \
    --duration 120 \
    --output "reports/ci_${TEST_ID}.html" \
    --log "logs/ci_${TEST_ID}.log"
```

### Nightly Performance Test

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
python3.14t -m pystress --config production.json \
    --threads 24 \
    --duration 600 \
    --output "reports/nightly_${DATE}.html"
```

### Debug Single Request

```bash
python3.14t -m pystress --config api.json \
    --single-request \
    --log debug.log
```

---

## 🎨 Report Features

The HTML report includes:

- ✅ **Target endpoint** - large, prominent display
- ✅ **Quick stats** - pass rate, RPS, total requests
- ✅ **Hardware info** - cores, processors, GIL status
- ✅ **Latency metrics** - min, avg, median, p90, p99, max
- ✅ **Baseline comparisons** - quick (5 reqs) + extended (if used)
- ✅ **Speedup calculations** - throughput, latency improvements
- ✅ **Status breakdown** - HTTP codes with badges
- ✅ **Modern design** - Bootstrap 5, responsive, green theme

---

## 🐛 Troubleshooting

### "Python 3.14 or higher is required"

You're using Python 3.12 or earlier. Install Python 3.14t.

### "GIL is ENABLED"

You have standard Python 3.14, not the free-threaded build.

**Fix:** Download `python-3.14.0t-amd64.zip` from python.org (note the **t** suffix).

### Low Performance / Sequential Execution

Check GIL status:
```bash
python -c "import sys; print(sys._is_gil_enabled())"
```

If `True`, you need Python 3.14t.

### Import Errors

Some packages may not work with free-threaded Python yet. Report issues to the package maintainers.

---

## 🔗 Links

- **Python 3.14 Downloads**: https://www.python.org/downloads/release/python-3140/
- **Free-Threading Docs**: https://docs.python.org/3.14/howto/free-threading-python.html
- **PEP 703**: https://peps.python.org/pep-0703/
- **Author**: [hammadabbasi.com](https://hammadabbasi.com)

---

## 📄 License

MIT License - see LICENSE file

---

## 👤 Author

**Hammad Abbasi**
- Website: [hammadabbasi.com](https://hammadabbasi.com)
- GitHub: [@hammadabbasi](https://github.com/hammadabbasi)

---

**Built for Python 3.14's free-threading revolution** 🚀
