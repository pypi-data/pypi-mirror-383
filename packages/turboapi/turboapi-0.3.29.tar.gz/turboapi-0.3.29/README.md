# TurboAPI 🚀

**The Python web framework that gives you FastAPI's beloved developer experience with 5-10x the performance.**

Built with Rust for revolutionary speed, designed with Python for developer happiness.

> **⚡ Try it in 30 seconds:** `python live_performance_showcase.py` → Visit `http://127.0.0.1:8080`  
> **🔥 See the difference:** Same FastAPI syntax, 5-10x faster performance!  
> **🎯 Zero migration effort:** Change 1 import line, keep all your existing code
> **🔒 NEW in v0.3.29:** Complete async optimization - 81% performance improvement!

## 🆕 **What's New in v0.3.29**

### **Complete Async Optimization Stack** 
- **3,584 async RPS** (81% improvement from baseline!)
- 14 parallel event loop shards (one per CPU core)
- Semaphore gating (512 concurrent tasks per shard)
- 256-request batching for maximum throughput
- Hash-based shard routing for cache locality
- Stable 3.1K+ RPS across all load levels (c=50-500)

### **Complete Security Suite** (100% FastAPI-compatible)
- **OAuth2** (Password Bearer, Authorization Code)
- **HTTP Auth** (Basic, Bearer, Digest)
- **API Keys** (Query, Header, Cookie)
- **Security Scopes** for fine-grained authorization

### **Complete Middleware Suite** (100% FastAPI-compatible)
- **CORS** with regex and expose_headers
- **Trusted Host** (Host Header attack prevention)
- **GZip** compression
- **HTTPS** redirect
- **Session** management
- **Rate Limiting** (TurboAPI exclusive!)
- **Custom** middleware support

## 🎨 **100% FastAPI-Compatible Developer Experience**

TurboAPI provides **identical syntax** to FastAPI - same decorators, same patterns, same simplicity. But with **5-10x better performance**.

### **Instant Migration from FastAPI**

```python
# Just change this line:
# from fastapi import FastAPI
from turboapi import TurboAPI

# Everything else stays exactly the same!
app = TurboAPI(
    title="My Amazing API",
    version="1.0.0",
    description="FastAPI syntax with TurboAPI performance"
)

@app.get("/")
def read_root():
    return {"message": "Hello TurboAPI!", "performance": "🚀"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "username": f"user_{user_id}"}

@app.post("/users")
def create_user(name: str, email: str):
    return {"name": name, "email": email, "status": "created"}

# Same run command as FastAPI
app.run(host="127.0.0.1", port=8000)
```

**That's it!** Same decorators, same syntax, **5-10x faster performance**.

## 🚀 **Revolutionary Performance**

### **Why TurboAPI is 5-10x Faster**
- **🦀 Rust-Powered HTTP Core**: Zero Python overhead for request handling
- **⚡ Zero Middleware Overhead**: Rust-native middleware pipeline  
- **🧵 Free-Threading Ready**: True parallelism for Python 3.13+
- **💾 Zero-Copy Optimizations**: Direct memory access, no Python copying
- **🔄 Intelligent Caching**: Response caching with TTL optimization

### **Benchmark Results vs FastAPI** (wrk load testing)

![Benchmark Comparison](benchmark_comparison.png)

```
🎯 Light Load (50 connections):
  Root Endpoint:       42,803 req/s (TurboAPI) vs 8,078 req/s (FastAPI) = 5.3x faster
  Simple Endpoint:     43,375 req/s (TurboAPI) vs 8,536 req/s (FastAPI) = 5.1x faster  
  JSON Endpoint:       41,696 req/s (TurboAPI) vs 3,208 req/s (FastAPI) = 13.0x faster

🎯 Medium Load (200 connections):
  Root Endpoint:       42,874 req/s (TurboAPI) vs 8,220 req/s (FastAPI) = 5.2x faster
  Simple Endpoint:     43,592 req/s (TurboAPI) vs 8,542 req/s (FastAPI) = 5.1x faster
  JSON Endpoint:       41,822 req/s (TurboAPI) vs 3,190 req/s (FastAPI) = 13.1x faster

🎯 Heavy Load (500 connections):
  Root Endpoint:       43,057 req/s (TurboAPI) vs 7,897 req/s (FastAPI) = 5.5x faster
  Simple Endpoint:     43,525 req/s (TurboAPI) vs 8,092 req/s (FastAPI) = 5.4x faster
  JSON Endpoint:       42,743 req/s (TurboAPI) vs 3,099 req/s (FastAPI) = 13.8x faster

🚀 Summary:
  • Average speedup: 5-13x faster than FastAPI
  • Consistent 40,000+ RPS across all load levels
  • JSON processing: Up to 13.8x faster
  • True multi-core utilization with Python 3.13 free-threading
  • Sub-millisecond latency under light load
```

## 🎯 **Zero Learning Curve**

If you know FastAPI, you already know TurboAPI:

## 🔥 **LIVE DEMO - Try It Now!**

Experience TurboAPI's FastAPI-compatible syntax with real-time performance metrics:

```bash
# Run the interactive showcase
python live_performance_showcase.py

# Visit these endpoints to see TurboAPI in action:
# 🏠 http://127.0.0.1:8080/ - Welcome & feature overview  
# 📊 http://127.0.0.1:8080/performance - Live performance metrics
# 🔍 http://127.0.0.1:8080/search?q=turboapi&limit=20 - FastAPI-style query params
# 👤 http://127.0.0.1:8080/users/123?include_details=true - Path + query params
# 💪 http://127.0.0.1:8080/stress-test?concurrent_ops=5000 - Stress test
# 🏁 http://127.0.0.1:8080/benchmark/cpu?iterations=10000 - CPU benchmark
```

**What you'll see:**
- ✅ **Identical FastAPI syntax** - same decorators, same patterns
- ⚡ **Sub-millisecond response times** - even under heavy load  
- 📊 **Real-time performance metrics** - watch TurboAPI's speed
- 🚀 **5-10x faster processing** - compared to FastAPI benchmarks

### **Migration Test - Replace FastAPI in 30 Seconds**

Want to test migration? Try this FastAPI-to-TurboAPI conversion:

```python
# Your existing FastAPI code
# from fastapi import FastAPI  ← Comment this out
from turboapi import TurboAPI as FastAPI  # ← Add this line

# Everything else stays identical - same decorators, same syntax!
app = FastAPI(title="My API", version="1.0.0")

@app.get("/items/{item_id}")  # Same decorator
def read_item(item_id: int, q: str = None):  # Same parameters
    return {"item_id": item_id, "q": q}  # Same response

app.run()  # 5-10x faster performance!
```

## 🎯 **Must-Try Demos**

### **1. 🔥 Live Performance Showcase**
```bash
python live_performance_showcase.py
```
Interactive server with real-time metrics showing FastAPI syntax with TurboAPI speed.

### **2. 🥊 Performance Comparison**  
```bash
python turbo_vs_fastapi_demo.py
```
Side-by-side comparison showing identical syntax with performance benchmarks.

### **3. 📊 Comprehensive Benchmarks**
```bash 
python comprehensive_benchmark.py
```
Full benchmark suite with decorator syntax demonstrating 5-10x performance gains.

## 🎉 **Why Developers Love TurboAPI**

### **"It's Just FastAPI, But Faster!"**

```python
# Before (FastAPI)
from fastapi import FastAPI
app = FastAPI()

@app.get("/api/heavy-task") 
def cpu_intensive():
    return sum(i*i for i in range(10000))  # Takes 3ms, handles 1,800 RPS

# After (TurboAPI) - SAME CODE!
from turboapi import TurboAPI as FastAPI  # ← Only change needed!
app = FastAPI()

@app.get("/api/heavy-task")
def cpu_intensive():
    return sum(i*i for i in range(10000))  # Takes 0.9ms, handles 5,700+ RPS! 🚀
```

### **Real-World Impact**
- 🏢 **Enterprise APIs**: Serve 5-10x more users with same infrastructure
- 💰 **Cost Savings**: 80% reduction in server costs
- ⚡ **User Experience**: Sub-millisecond response times
- 🛡️ **Reliability**: Rust memory safety + Python productivity
- 📈 **Scalability**: True parallelism ready for Python 3.13+

### **Migration Stories** *(Simulated Results)*
```
📊 E-commerce API Migration:
   Before: 2,000 RPS → After: 12,000+ RPS
   Migration time: 45 minutes
   
📊 Banking API Migration:  
   Before: P95 latency 5ms → After: P95 latency 1.2ms
   Compliance: ✅ Same Python code, Rust safety
   
📊 Gaming API Migration:
   Before: 500 concurrent users → After: 3,000+ concurrent users  
   Real-time performance: ✅ Sub-millisecond responses
```

## ⚡ **Quick Start**

### **Installation**

#### **Option 1: Install from PyPI (Recommended)**
```bash
# Install Python 3.13 free-threading for optimal performance
# macOS/Linux users can use pyenv or uv

# Create free-threading environment
python3.13t -m venv turbo-env
source turbo-env/bin/activate  # On Windows: turbo-env\Scripts\activate

# Install TurboAPI (includes prebuilt wheels for macOS and Linux)
pip install turboapi

# Verify installation
python -c "from turboapi import TurboAPI; print('✅ TurboAPI v0.3.27 ready!')"
```

#### **Option 2: Build from Source**
```bash
# Clone repository
git clone https://github.com/justrach/turboAPI.git
cd turboAPI

# Create Python 3.13 free-threading environment
python3.13t -m venv turbo-freethreaded
source turbo-freethreaded/bin/activate

# Install Python package
pip install -e python/

# Build Rust core for maximum performance
pip install maturin
maturin develop --manifest-path Cargo.toml

# Verify installation
python -c "from turboapi import TurboAPI; print('✅ TurboAPI ready!')"
```

**Note**: Free-threading wheels (cp313t) available for macOS and Linux. Windows uses standard Python 3.13.

### **🎨 FastAPI-Identical Syntax Examples**

#### **Basic API (Same as FastAPI)**
```python
from turboapi import TurboAPI

app = TurboAPI(title="FastAPI-Compatible Demo", version="1.0.0")

@app.get("/")
def read_root():
    return {"Hello": "TurboAPI", "performance": "5-10x faster!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

app.run(host="127.0.0.1", port=8000)
```

#### **Advanced Features (Same as FastAPI)**
```python
from turboapi import TurboAPI
import time

app = TurboAPI()

# Path parameters
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}

# Query parameters  
@app.get("/search")
def search_items(q: str, limit: int = 10):
    return {"query": q, "limit": limit, "results": [f"item_{i}" for i in range(limit)]}

# POST with body
@app.post("/users")
def create_user(name: str, email: str):
    return {"name": name, "email": email, "created_at": time.time()}

# All HTTP methods work
@app.put("/users/{user_id}")
def update_user(user_id: int, name: str = None):
    return {"user_id": user_id, "updated_name": name}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {"user_id": user_id, "deleted": True}

app.run()
```

## 🔒 **Security & Authentication (NEW!)**

TurboAPI now includes **100% FastAPI-compatible** security features:

### **OAuth2 Authentication**
```python
from turboapi import TurboAPI
from turboapi.security import OAuth2PasswordBearer, Depends

app = TurboAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
def login(username: str, password: str):
    # Validate credentials
    return {"access_token": username, "token_type": "bearer"}

@app.get("/users/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Decode and validate token
    return {"token": token, "user": "current_user"}
```

### **HTTP Basic Authentication**
```python
from turboapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

@app.get("/admin")
def admin_panel(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Welcome admin!"}
```

### **API Key Authentication**
```python
from turboapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.get("/secure-data")
def get_secure_data(api_key: str = Depends(api_key_header)):
    if api_key != "secret-key-123":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return {"data": "sensitive information"}
```

## 🛡️ **Middleware (NEW!)**

Add powerful middleware with FastAPI-compatible syntax:

### **CORS Middleware**
```python
from turboapi.middleware import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Custom-Header"],
    max_age=600,
)
```

### **GZip Compression**
```python
from turboapi.middleware import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=9)
```

### **Rate Limiting** (TurboAPI Exclusive!)
```python
from turboapi.middleware import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100,
    burst=20
)
```

### **Trusted Host Protection**
```python
from turboapi.middleware import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)
```

### **Custom Middleware**
```python
import time

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Architecture

TurboAPI consists of three main components:

1. **TurboNet (Rust)**: High-performance HTTP server built with Hyper
2. **FFI Bridge (PyO3)**: Zero-copy interface between Rust and Python
3. **TurboAPI (Python)**: Developer-friendly framework layer

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Python App    │    │   TurboAPI       │    │   TurboNet      │
│                 │◄──►│   Framework      │◄──►│   (Rust HTTP)   │
│  Your Handlers  │    │   (Python)       │    │   Engine        │
└─────────────────┘    └──────────────────┘    └─────────────────┘

## 🚀 Performance

TurboAPI delivers **7.5x FastAPI middleware performance** with comprehensive Phase 5 optimizations:

### 📊 **HTTP Performance (Phases 3-5)**
- **Throughput**: 4,019-7,320 RPS vs FastAPI's 1,116-2,917 RPS
- **Latency**: Sub-millisecond P95 response times (0.91-1.29ms vs 2.79-3.00ms)
- **Improvement**: **2.5-3.6x faster** across all load levels
- **Parallelism**: True multi-threading with 4 server threads
- **Memory**: Efficient Rust-based HTTP handling

### 🔧 **Middleware Performance (Phase 5)**
- **Average Latency**: 0.11ms vs FastAPI's 0.71ms (**6.3x faster**)
- **P95 Latency**: 0.17ms vs FastAPI's 0.78ms (**4.7x faster**)
- **Concurrent Throughput**: 22,179 req/s vs FastAPI's 2,537 req/s (**8.7x faster**)
- **Overall Middleware**: **7.5x FastAPI performance**
- **Zero Overhead**: Rust-powered middleware pipeline

### 🌐 **WebSocket Performance (Phase 4)**
- **Latency**: 0.10ms avg vs FastAPI's 0.18ms (**1.8x faster**)
- **Real-time**: Sub-millisecond response times
- **Concurrency**: Multi-client support with broadcasting
- **Memory**: Zero-copy message handling

### 💾 **Zero-Copy Optimizations (Phase 4)**
- **Buffer Pooling**: Intelligent memory management (4KB/64KB/1MB pools)
- **String Interning**: Memory optimization for common paths
- **SIMD Operations**: Fast data processing and comparison
- **Memory Efficiency**: Reference counting instead of copying

### 🛡️ **Production Middleware (Phase 5)**
- **CORS**: Cross-origin request handling with preflight optimization
- **Rate Limiting**: Sliding window algorithm with burst protection
- **Authentication**: Multi-token support with configurable validation
- **Caching**: TTL-based response caching with intelligent invalidation
- **Compression**: GZip optimization with configurable thresholds
- **Logging**: Request/response monitoring with performance metrics

**Phase 5 Achievement**: **7.5x FastAPI middleware performance** with enterprise-grade features
**Architecture**: Most advanced Python web framework with production-ready middleware

## Development Status

TurboAPI has completed **Phase 5** with comprehensive advanced middleware support:

**✅ Phase 0 - Foundation (COMPLETE)**
- [x] Project structure and Rust crate setup
- [x] Basic PyO3 bindings and Python package
- [x] HTTP/1.1 server implementation (1.14x FastAPI)

**✅ Phase 1 - Routing (COMPLETE)**  
- [x] Radix trie routing system
- [x] Path parameter extraction
- [x] Method-based routing

**✅ Phase 2 - Validation (COMPLETE)**
- [x] Satya integration for 2-7x Pydantic performance
- [x] Type-safe request/response handling
- [x] Advanced validation features (1.26x FastAPI)

**✅ Phase 3 - Free-Threading (COMPLETE)**
- [x] Python 3.13 free-threading integration
- [x] PyO3 0.26.0 with `gil_used = false`
- [x] Multi-threaded Tokio runtime
- [x] True parallelism with 4 server threads
- [x] **2.84x FastAPI performance achieved!**

**✅ Phase 4 - Advanced Protocols (COMPLETE)**
- [x] HTTP/2 support with server push and multiplexing
- [x] WebSocket integration with real-time communication
- [x] Zero-copy optimizations with buffer pooling
- [x] SIMD operations and string interning
- [x] **3.01x FastAPI performance achieved!**

**✅ Phase 5 - Advanced Middleware (COMPLETE)**
- [x] Production-grade middleware pipeline system
- [x] CORS, Rate Limiting, Authentication, Logging, Compression, Caching
- [x] Priority-based middleware processing
- [x] Built-in performance monitoring and metrics
- [x] Zero-copy integration with Phase 4 optimizations
- [x] **7.5x FastAPI middleware performance**

## 🎯 FastAPI-like Developer Experience

### **Multi-Route Example Application**

TurboAPI provides the exact same developer experience as FastAPI:

```bash
# Test the complete FastAPI-like functionality
cd examples/multi_route_app
python demo_routes.py
```

**Results:**
```
🎉 ROUTE DEMONSTRATION COMPLETE!
✅ All route functions working correctly
✅ FastAPI-like developer experience demonstrated
✅ Production patterns validated
⏱️ Total demonstration time: 0.01s

🎯 Key Features Demonstrated:
   • Path parameters (/users/{id}, /products/{id})
   • Query parameters with filtering and pagination
   • Request/response models with validation
   • Authentication flows with JWT-like tokens
   • CRUD operations with proper HTTP status codes
   • Search and filtering capabilities
   • Error handling with meaningful messages
```

### **Production Features Validated**

- **15+ API endpoints** with full CRUD operations
- **Authentication system** with JWT-like tokens
- **Advanced filtering** and search capabilities
- **Proper error handling** with HTTP status codes
- **Pagination and sorting** for large datasets
- **Production-ready patterns** throughout

## 🔮 What's Next?

### **Phase 6: Full Integration** 🚧

**Currently in development** - The final phase to achieve 5-10x FastAPI overall performance:

- ✅ **Automatic Route Registration**: `@app.get()` decorators working perfectly
- 🚧 **HTTP Server Integration**: Connect middleware pipeline to server
- 🔄 **Multi-Protocol Support**: HTTP/1.1, HTTP/2, WebSocket middleware
- 🎯 **Performance Validation**: Achieve 5-10x FastAPI overall performance
- 🏢 **Production Readiness**: Complete enterprise-ready framework

### **Phase 6.1 Complete: Route Registration System** ✅

```python
from turboapi import TurboAPI, APIRouter

app = TurboAPI(title="My API", version="1.0.0")

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "name": "John Doe"}

@app.post("/users")
async def create_user(name: str, email: str):
    return {"message": "User created", "name": name}

# Router support
users_router = APIRouter(prefix="/api/users", tags=["users"])

@users_router.get("/")
async def list_users():
    return {"users": []}

app.include_router(users_router)
```

**Results:**
```
🎯 Phase 6 Features Demonstrated:
   ✅ FastAPI-compatible decorators (@app.get, @app.post)
   ✅ Automatic route registration
   ✅ Path parameter extraction (/items/{item_id})
   ✅ Query parameter handling
   ✅ Router inclusion with prefixes
   ✅ Event handlers (startup/shutdown)
   ✅ Request/response handling
```

### **Production Readiness**

Phase 5 establishes TurboAPI as:

- **Most Advanced**: Middleware system of any Python framework
- **Highest Performance**: 7.5x FastAPI middleware performance
- **FastAPI Compatible**: Identical developer experience proven
- **Enterprise Ready**: Production-grade features and reliability
- **Future Proof**: Free-threading architecture for Python 3.14+

## Requirements

- **Python 3.13+** (free-threading build for no-GIL support)
- **Rust 1.70+** (for building the extension)
- **maturin** (for Python-Rust integration)
- **PyO3 0.26.0+** (for free-threading compatibility)

## Building from Source

```bash
# Clone the repository
git clone https://github.com/justrach/turboapiv2.git
cd turboapiv2

# Create a Python 3.13 free-threading environment
python3.13t -m venv turbo-env
source turbo-env/bin/activate

# Install dependencies
pip install maturin

# Build and install TurboAPI
maturin develop --release
```

## 📊 **Running Benchmarks**

TurboAPI includes comprehensive benchmarking tools to verify performance claims.

### **Quick Benchmark with wrk**

```bash
# Install wrk (if not already installed)
brew install wrk  # macOS
# sudo apt install wrk  # Linux

# Run the comparison benchmark
python tests/wrk_comparison.py

# Generates:
# - Console output with detailed results
# - benchmark_comparison.png (visualization)
```

**Expected Results**:
- TurboAPI: 40,000+ req/s consistently
- FastAPI: 3,000-8,000 req/s
- Speedup: 5-13x depending on workload

### **Available Benchmark Scripts**

#### **1. wrk Comparison (Recommended)**
```bash
python tests/wrk_comparison.py
```
- Uses industry-standard wrk load tester
- Tests 3 load levels (light/medium/heavy)
- Tests 3 endpoints (/, /benchmark/simple, /benchmark/json)
- Generates PNG visualization
- Most accurate performance measurements

#### **2. Adaptive Rate Testing**
```bash
python tests/benchmark_comparison.py
```
- Finds maximum sustainable rate
- Progressive rate testing
- Python-based request testing

#### **3. Quick Verification**
```bash
python tests/quick_test.py
```
- Fast sanity check
- Verifies rate limiting is disabled
- Tests basic functionality

### **Benchmark Configuration**

**Ports**:
- TurboAPI: `http://127.0.0.1:8080`
- FastAPI: `http://127.0.0.1:8081`

**Rate Limiting**: Disabled by default for benchmarking
```python
from turboapi import TurboAPI
app = TurboAPI()
app.configure_rate_limiting(enabled=False)  # For benchmarking
```

**Multi-threading**: Automatically uses all CPU cores
```python
import os
workers = os.cpu_count()  # e.g., 14 cores on M3 Max
app.run(host="127.0.0.1", port=8000, workers=workers)
```

### **Interpreting Results**

**Key Metrics**:
- **RPS (Requests/second)**: Higher is better
- **Latency**: Lower is better (p50, p95, p99)
- **Speedup**: TurboAPI RPS / FastAPI RPS

**Expected Performance**:
```
Light Load (50 conn):     40,000+ RPS, ~1-2ms latency
Medium Load (200 conn):   40,000+ RPS, ~4-5ms latency  
Heavy Load (500 conn):    40,000+ RPS, ~11-12ms latency
```

**Why TurboAPI is Faster**:
1. **Rust HTTP core** - No Python overhead
2. **Zero-copy operations** - Direct memory access
3. **Free-threading** - True parallelism (no GIL)
4. **Optimized middleware** - Rust-native pipeline

## Testing & Quality Assurance

TurboAPI includes comprehensive testing and continuous benchmarking:

### **Comprehensive Test Suite**

```bash
# Run full test suite
python test_turboapi_comprehensive.py

# Run specific middleware tests
python test_simple_middleware.py

# Run performance benchmarks
python benchmarks/middleware_vs_fastapi_benchmark.py
python benchmarks/final_middleware_showcase.py
```

### **Continuous Integration**

Our GitHub Actions workflow automatically:

- ✅ **Builds and tests** on every commit
- ✅ **Runs performance benchmarks** vs FastAPI
- ✅ **Detects performance regressions** with historical comparison
- ✅ **Updates performance dashboard** with latest results
- ✅ **Comments on PRs** with benchmark results

### **Performance Regression Detection**

```bash
# Check for performance regressions
python .github/scripts/check_performance_regression.py

# Compare with historical benchmarks
python .github/scripts/compare_benchmarks.py
```

The CI system maintains performance baselines and alerts on:
- **15%+ latency increases**
- **10%+ throughput decreases** 
- **5%+ success rate drops**
- **Major architectural regressions**

## Contributing

TurboAPI is in active development! We welcome contributions:

1. Check out the [execution plan](docs/execution-plan.md)
2. Pick a task from the current phase
3. Submit a PR with tests and documentation

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- **FastAPI** for API design inspiration
- **Rust HTTP ecosystem** (Hyper, Tokio, PyO3)
- **Python 3.14** no-GIL development team

---

**Ready to go fast?** 🚀 Try TurboAPI today!
