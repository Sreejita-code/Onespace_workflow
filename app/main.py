from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <-- Add this import
from contextlib import asynccontextmanager
from app.shared.db.mongo import init_db
from app.modules.auth.router import router as auth_router
from app.modules.endpoints.router import router as endpoints_router
from app.modules.workflow.router import router as workflow_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await init_db()
    yield
    # Shutdown logic (if any) goes here

app = FastAPI(
    title="Workflow Builder Admin API", 
    description="Modular monolith API for enterprise chatbot workflows.",
    lifespan=lifespan
)

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Allows all origins
    allow_credentials=False, # Must be False when allow_origins is ["*"]
    allow_methods=["*"],     # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allows all headers
)
# --------------------------

app.include_router(auth_router, prefix="/api/auth")
app.include_router(endpoints_router, prefix="/api/endpoints")
app.include_router(workflow_router, prefix="/api/workflows")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": "development"}