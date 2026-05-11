import logging

# ── Central logging configuration (imported from logger.py) ────────────────────
from logger import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from database import engine, Base
from router import router as customer_router, counts_router
 
# ── Create tables if they don't exist yet ──────────────────────────────────────
# In production with seed.sql, tables already exist — this is a safety net.
Base.metadata.create_all(bind=engine)

# ── Lifespan Context Manager (Factor 9: Disposability) ─────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    start_time = time.time()
    logger.info("🟢 Application starting up...")
    logger.info("Startup completed in %.4f seconds. Ready to serve requests.", time.time() - start_time)
    
    yield  # Running phase: handles API requests
    
    # Shutdown phase
    logger.info("🔴 Application shutting down...")
    engine.dispose()
    logger.info("Database connections closed gracefully (engine.dispose()).")

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Customer API",
    description="A modular FastAPI service for managing customers, orders, and payments.",
    version="1.0.0",
    lifespan=lifespan,
)
 
# ── Global exception handler (logs any unhandled 500 errors) ──────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s — %s", request.method, request.url, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
 
# ── Register routers ───────────────────────────────────────────────────────────
app.include_router(customer_router)
app.include_router(counts_router)
 
logger.info("Customer API started. Docs at http://localhost:8000/docs")
 
 
@app.get("/", tags=["Health"])
def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok", "message": "Customer API is running."}