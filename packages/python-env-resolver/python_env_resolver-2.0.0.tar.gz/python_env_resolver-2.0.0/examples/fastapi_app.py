"""
FastAPI example showing module-level config loading with from_env().

This demonstrates the Pythonic pattern:
- Load config at module import time (no startup events needed)
- Works with uvicorn/hypercorn (event loop safe)
- Clean, synchronous code

Run with:
    export DATABASE_URL="postgresql://localhost/mydb"
    export API_KEY="secret123"
    uvicorn examples.fastapi_app:app --reload

Or with .env:
    uvicorn examples.fastapi_app:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel

from python_env_resolver import from_env


class AppConfig(BaseModel):
    """Application configuration loaded from environment variables."""

    database_url: str
    api_key: str
    debug: bool = False
    port: int = 8000


# ✅ Load config at module import time
# This works even when uvicorn imports the module!
# from_env() detects the running event loop and executes in a thread
config = from_env(AppConfig)

print(f"✅ Config loaded: database_url={config.database_url}, debug={config.debug}")

# Create FastAPI app - config is already available!
app = FastAPI(
    title="python-env-resolver FastAPI Demo",
    debug=config.debug,
)


@app.get("/")
def root():
    """Root endpoint showing config is available."""
    return {
        "message": "Config loaded at module import time!",
        "database_url": config.database_url,
        "debug": config.debug,
        "port": config.port,
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "config_loaded": config is not None,
    }


@app.get("/config")
def get_config():
    """Get current configuration (excluding secrets)."""
    return {
        "database_url": config.database_url,
        "debug": config.debug,
        "port": config.port,
        "api_key": "***" + config.api_key[-4:] if len(config.api_key) > 4 else "***",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=config.port)

