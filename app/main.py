from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, heartbeat, vault
from app.database import engine, Base

app = FastAPI(
    title="Dead Man's Switch API",
    description="Zero-Knowledge Dead Man's Switch Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(heartbeat.router)
app.include_router(vault.router)


@app.on_event("startup")
async def startup():
    # Create tables (in production, use Alembic migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "Dead Man's Switch API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    """Test endpoint to verify OpenAPI schema generation"""
    return app.openapi()
