from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.health import router as health_router
from server.routes.cases import router as cases_router
from server.routes.customers import router as customers_router
from server.routes.knowledge_base import router as knowledge_base_router
from server.routes.diagnostics import router as diagnostics_router
from server.routes.overview import router as overview_router
from server.routes.ai import router as ai_router

app = FastAPI(
    title="ResolutionOps API",
    version="0.1.0",
    description="AI-powered customer issue investigation platform",
)

# CORS — allow Vite dev server in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(health_router, prefix="/api")
app.include_router(cases_router, prefix="/api")
app.include_router(customers_router, prefix="/api")
app.include_router(knowledge_base_router, prefix="/api")
app.include_router(diagnostics_router, prefix="/api")
app.include_router(overview_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
