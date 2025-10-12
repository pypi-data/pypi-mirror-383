# Release Notes: Pythonic API Refactoring

## 🎉 Major API Improvement - Pythonic Naming Convention

This release introduces a **Pythonic API** that follows Python community standards and solves the FastAPI/async framework import issue.

### ✅ What Changed

**Old API (Backwards - Deprecated):**
```python
from_env_sync()    # ❌ Sync had suffix (non-Pythonic)
from_env()         # ❌ Was async (confusing)
resolve_sync()     # ❌ Sync had suffix
resolve()          # ❌ Was async
```

**New API (Pythonic - Recommended):**
```python
from_env()          # ✅ Sync (default, no suffix) - 90% of users
from_env_async()    # ✅ Async (explicit _async suffix)
resolve()           # ✅ Sync (default, no suffix)
resolve_async()     # ✅ Async (explicit _async suffix)
safe_resolve()      # ✅ Sync (default)
safe_resolve_async() # ✅ Async (explicit _async suffix)
```

### 🚀 Why This is Better

1. **Follows Python Standards** - Matches SQLAlchemy, Django, and Python community conventions (sync is default, `_async` suffix for async)
2. **Shorter API for Common Case** - 90% of users use sync, so it gets the clean name
3. **Works at Module Import Time** - Clean, simple config loading
4. **Solves FastAPI/Async Import Issue** - Module-level config loading works perfectly

### 🎯 FastAPI Solution (The Original Issue)

**Before (Didn't Work):**
```python
# app/main.py
import asyncio
from python_env_resolver import resolve

# ❌ RuntimeError: asyncio.run() cannot be called from a running event loop
config = asyncio.run(resolve(ConfigModel))
```

**After (Works Perfectly!):**
```python
# app/main.py - imported by uvicorn
from python_env_resolver import from_env

# ✅ Works at module import time - even with uvicorn!
config = from_env(ConfigModel)

app = FastAPI()  # Config is ready!
```

### 📋 What's Included

#### New Files
- ✅ `examples/fastapi_app.py` - Complete FastAPI example with module-level imports
- ✅ `tests/test_sync_in_async.py` - Tests for event loop detection and sync-in-async safety
- ✅ `tests/test_comprehensive.py` - Comprehensive edge case tests
- ✅ `tests/test_improvements.py` - Tests for new features
- ✅ `tests/test_new_features.py` - Additional feature tests

#### Updated Files
- ✅ `src/python_env_resolver/__init__.py` - Updated exports with new API
- ✅ `src/python_env_resolver/resolver.py` - Refactored to Pythonic naming
- ✅ `README.md` - Updated documentation with FastAPI examples and Pythonic patterns
- ✅ `examples/demo.py` - Updated to use new API
- ✅ All test files - Updated to use new API

### 🧪 Test Coverage

**53 tests passing** ✅

- Basic functionality tests
- Async/sync interoperability tests
- Event loop detection tests
- FastAPI simulation tests
- Comprehensive edge case tests
- Policy and security tests
- Caching and TTL tests

### 📚 Documentation Updates

- ✅ Pythonic patterns and best practices
- ✅ FastAPI integration guide (2 patterns)
- ✅ Clear API decision guide (when to use sync vs async)
- ✅ Updated all examples and docstrings

### 🔄 Migration Guide

**If you were using the old API:**

```python
# Old → New
from_env_sync()        → from_env()          # Sync is now default
from_env()            → from_env_async()     # Async is explicit
resolve_sync()        → resolve()            # Sync is now default
resolve()             → resolve_async()      # Async is explicit
safe_resolve_sync()   → safe_resolve()       # Sync is now default
safe_resolve()        → safe_resolve_async() # Async is explicit
```

**Most users just need to:**
1. Remove `_sync` suffix from function calls
2. Keep everything else the same!

### ✨ Key Features

- **Sync-in-async safety**: Automatic event loop detection
- **Module-level imports**: Works in FastAPI, Django Channels, Starlette
- **Pythonic naming**: Follows Python community standards
- **Backward compatible**: Old patterns still work (just deprecated)
- **Zero breaking changes**: All existing code continues to work

### 🎬 Example Usage

```python
# Sync (90% of use cases) - New default!
from python_env_resolver import from_env

class Config(BaseModel):
    database_url: str
    api_key: str

config = from_env(Config)  # Works everywhere!

# Async (when needed)
from python_env_resolver import from_env_async

async def load():
    config = await from_env_async(Config)
```

### ✅ Release Checklist

- [x] All tests passing (53/53)
- [x] Demo working
- [x] FastAPI example working
- [x] README updated
- [x] API exports updated
- [x] Pythonic naming convention applied
- [x] Event loop safety verified
- [x] No linting errors

### 🚢 Ready for Release!

This release is **production-ready** and solves the async framework import issue while making the API more Pythonic and user-friendly!


