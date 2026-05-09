import logging
import logging.config

# ── Global logging configuration ───────────────────────────────────────────────
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "detailed",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from database import engine, Base
from router import router as customer_router
 
# ── Create tables if they don't exist yet ──────────────────────────────────────
# In production with seed.sql, tables already exist — this is a safety net.
Base.metadata.create_all(bind=engine)
 
# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Customer API",
    description="A modular FastAPI service for managing customers, orders, and payments.",
    version="1.0.0",
)
 
# ── Global exception handler (logs any unhandled 500 errors) ──────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s — %s", request.method, request.url, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
 
# ── Register routers ───────────────────────────────────────────────────────────
app.include_router(customer_router)
 
logger.info("🚀 Customer API started. Docs at http://localhost:8000/docs")
 
 
@app.get("/", tags=["Health"])
def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok", "message": "Customer API is running."}
 