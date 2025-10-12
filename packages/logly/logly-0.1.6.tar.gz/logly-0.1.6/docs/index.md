---
title: Logly - High-Performance Python Logging Library
description: Rust-powered logging for Python with async I/O, beautiful output, and 3x faster performance than standard logging. Features callbacks, and smart rotation.
keywords: python, logging, rust, async, performance, loguru, pyo3, high-performance
---

<div align="center">

  <img src="assets/logly-logo.png" alt="Logly Logo" width="400" />
  <p><em>Rust-powered, Loguru-like logging for Python</em></p>

  <a href="https://pypi.org/project/logly/"><img src="https://img.shields.io/pypi/v/logly.svg" alt="PyPI"></a>
  <a href="https://pypistats.org/packages/logly"><img src="https://img.shields.io/pypi/dm/logly.svg" alt="Downloads"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-%3E%3D3.10-brightgreen.svg" alt="Python"></a>
  <a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/license/muhammad-fiaz/logly.svg" alt="License"></a>
</div>

---

## Overview

**Logly** is a high-performance logging library for Python, powered by Rust. It combines the familiar Loguru-like API with the performance and safety guarantees of Rust.

Built with a modular Rust backend using PyO3/Maturin, Logly provides fast logging while maintaining memory safety and thread safety through Rust's ownership system.

!!! warning "Active Development"
    Logly is actively developed. Performance continues to improve with each release.

!!! success "Jupyter/Colab Support - Guaranteed Output"
    **NEW:** Logly now works seamlessly in Jupyter Notebooks and Google Colab with **robust fallback mechanism**! 
    
    - ✅ Logs display correctly in notebook output cells (Python's sys.stdout)
    - ✅ **Always visible**: Automatic fallback to Rust println! if Python stdout fails
    - ✅ Works in all environments - notebooks, terminals, servers, and edge cases
    
    See [Issue #76](https://github.com/muhammad-fiaz/logly/issues/76) and [Jupyter/Colab Examples](examples/jupyter-colab.md) for details.

!!! note "Note"
    The Documentation is up-to-date with the main branch so some features may be missing for the old releases on PyPI. also the docs are improving continuously. if you find any issues please report them on GitHub.


### 🎯 Why Logly?

Logly combines the simplicity of Python with the performance and safety of Rust, providing:

- **High Performance**: Rust-powered backend with optimized data structures
- **Memory Safety**: No data races, guaranteed thread safety
- **Comprehensive Solution**: Full-featured logging with async, rotation, filtering, and callbacks
- **Developer Friendly**: Intuitive API inspired by Loguru

### ✨ Key Features

- 🚀 **Rust-Powered Backend**: High-performance logging with async buffering
- 📦 **Modular Architecture**: Clean separation (backend, config, format, utils)
- 🔄 **Async Logging**: Background thread writing with configurable buffering
- 📋 **Structured JSON**: Native JSON support with custom fields and pretty printing
- 🎨 **Colored Levels**: Automatic color mapping (TRACE=cyan, SUCCESS=green, WARNING=yellow, FAIL=magenta, etc.)
- ⚙️ **Per-Level Controls**: Fine-grained control over console output, timestamps, colors, and storage
- ⌛ **Time Format Specs** (NEW in v0.1.6): Customize timestamps with Loguru-style patterns like `{time:YYYY-MM-DD HH:mm:ss}`
- 🐍 **Python 3.14 Support** (NEW in v0.1.6): Full compatibility with Python 3.14
- �🔧 **Smart Rotation**: Time-based (daily/hourly/minutely) and size-based rotation
- 🗜️ **Compression**: Built-in gzip and zstd compression for rotated files
- 🎯 **Multi-Sink**: Multiple outputs with independent filtering and formatting
- 🔍 **Rich Filtering**: Filter by level, module, or function name
- 📞 **Callbacks**: Custom log processing with async execution, color styling, and filename/line number tracking
- 🆕 **FAIL Level**: New log level for operation failures (v0.1.5)
- 🛡️ **Memory Safe**: Rust's ownership system prevents data races
- 🧵 **Thread Safe**: Lock-free operations with optimized synchronization

---

## Quick Navigation

### Core Documentation

- **[Quick Start Guide](quickstart.md)** - Get up and running in 5 minutes with basic setup and examples
- **[API Reference](api-reference/index.md)** - Complete documentation of all methods and configuration options
- **[Examples](examples/index.md)** - Practical code examples for common logging scenarios
- **[Installation Guide](installation.md)** - Install Logly with pip, uv, or poetry

### Advanced Topics

- **[Configuration Guide](guides/configuration.md)** - Advanced configuration patterns and production setups
- **[Troubleshooting](guides/troubleshooting.md)** - Common issues and solutions for debugging problems
- **[Changelog](changelog.md)** - See what's new in each version

---

## Quick Start

### Installation

```bash
pip install logly
```

### Basic Usage

**NEW in v0.1.5:** No configuration needed - just import and log!

```python
from logly import logger

# That's it! Start logging immediately with colored output
logger.info("Application started", version="1.0.0")     # ✅ White
logger.success("Database connected")                    # ✅ Green
logger.warning("Cache is full")                         # ✅ Yellow
logger.error("Failed to connect", retry_count=3)        # ✅ Red
logger.fail("Authentication failed", user="alice")      # ✅ Magenta (NEW)
```

**Why it works:**
- Logger is auto-configured on import (since v0.1.5)
- Default settings: `console=True`, `auto_sink=True`, `color=True`
- Console sink created automatically with colored levels
- **File sinks are NEVER automatic** - add them explicitly

### Advanced: Add File Sinks

```python
from logly import logger

# Console already works, now add file logging
logger.add("logs/app.log", rotation="daily", retention=7)
logger.add("logs/errors.log", filter_min_level="ERROR")

logger.info("Logs to both console and files")

# Cleanup when done
logger.complete()
```

---

## Core Concepts

### 1. Multiple Sinks

Route logs to different destinations with independent configurations:

```python
# Console for development
logger.add("console")

# Daily rotated files for production
logger.add("logs/app.log", rotation="daily", retention=30)

# Errors to separate file
logger.add("logs/errors.log", filter_min_level="ERROR")
```

### 2. Structured Logging

Automatically capture structured data:

```python
# Text mode: "User logged in user=alice ip=192.168.1.1"
logger.info("User logged in", user="alice", ip="192.168.1.1")

# JSON mode: {"timestamp": "...", "level": "INFO", "message": "...", "fields": {...}}
logger.configure(json=True)
logger.info("User logged in", user="alice", ip="192.168.1.1")
```

### 3. Context Management

Bind persistent context to log messages:

```python
# Create context logger
request_logger = logger.bind(request_id="r-123", user="alice")

# All logs include context
request_logger.info("Request started")  # Includes request_id and user
request_logger.error("Request failed")  # Context preserved

# Temporary context
with request_logger.contextualize(step="validation"):
    request_logger.debug("Validating input")  # Includes step field
```

### 4. Async Callbacks

React to log events in real-time without blocking:

```python
def alert_on_critical(record):
    if record.get("level") == "CRITICAL":
        send_notification(f"Critical error: {record['message']}")

callback_id = logger.add_callback(alert_on_critical)

# Callbacks execute in background threads
logger.critical("System out of memory")  # Alert sent asynchronously
```

---

## Architecture

```mermaid
graph TB
    A[Python Application] --> B[_LoggerProxy]
    B --> C[Context Binding]
    C --> D[PyLogger Rust]
    D --> E[Async Writer Thread]
    D --> F[Callback Threads]
    E --> G[File Sinks]
    E --> H[Console Sink]
    F --> I[User Callbacks]
```

### Components

- **_LoggerProxy** - Python wrapper with context binding support
- **PyLogger** - Rust core with tracing backend
- **Async Writer** - Background thread for non-blocking file I/O
- **Callback System** - Thread pool for async event handlers
- **Sink Management** - Multiple output destinations with filters

---

## Use Cases

### Web Applications

```python
from logly import logger
from fastapi import FastAPI, Request

app = FastAPI()
logger.add("console")
logger.add("logs/api.log", rotation="daily", retention=7)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_logger = logger.bind(
        request_id=request.headers.get("X-Request-ID"),
        method=request.method,
        path=request.url.path
    )
    
    request_logger.info("Request received")
    response = await call_next(request)
    request_logger.info("Response sent", status_code=response.status_code)
    
    return response
```

### Data Processing Pipelines

```python
from logly import logger

logger.configure(json=True)
logger.add("logs/pipeline.log", size_limit="100MB", retention=10)

pipeline_logger = logger.bind(job_id="job-123", pipeline="etl")

for batch in process_data():
    with pipeline_logger.contextualize(batch_id=batch.id):
        pipeline_logger.info("Processing batch", records=len(batch))
        try:
            transform(batch)
            load(batch)
            pipeline_logger.success("Batch complete", duration=batch.elapsed)
        except Exception as e:
            pipeline_logger.exception("Batch failed")
```

### Monitoring and Alerting

```python
from logly import logger
import requests

def forward_to_monitoring(record):
    """Forward logs to external monitoring system"""
    if record.get("level") in ["ERROR", "CRITICAL"]:
        requests.post("https://monitoring.example.com/logs", json=record)

logger.add_callback(forward_to_monitoring)

# All errors automatically forwarded
logger.error("Database connection lost", retry_count=3)
logger.critical("Service unresponsive")
```



---

## 🚀 Quick Start

Get up and running in 5 minutes

[Quick Start Guide](quickstart.md)

## 📚 API Reference

Complete documentation of all methods

[API Reference](api-reference/index.md)

## 📝 Changelog

See what's new in each version

[View Changelog](changelog.md)

## ⬇️ Installation

Install Logly with pip, uv, or poetry

[Installation Guide](installation.md)

---

## Community

- 🐛 [Report Issues](https://github.com/muhammad-fiaz/logly/issues)
- 💡 [Feature Requests](https://github.com/muhammad-fiaz/logly/discussions)
- 📖 [Contributing Guide](https://github.com/muhammad-fiaz/logly/blob/main/CONTRIBUTING.md)
- ⭐ [Star on GitHub](https://github.com/muhammad-fiaz/logly)

---

## License

Logly is licensed under the [MIT License](https://github.com/muhammad-fiaz/logly/blob/main/LICENSE).
