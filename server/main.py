from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.health import router as health_router

app = FastAPI(
    title="ResolutionOps API",
    version="0.1.0",
    description="AI-powered customer issue investigation platform",
)

# CORS — allow Vite dev server in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(health_router, prefix="/api")
