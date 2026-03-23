from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import analyze, simulate

app = FastAPI(
    title="Food Label Analyzer",
    description="AI-Powered FSSAI Compliance Checker",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api")
app.include_router(simulate.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Food Label Analyzer API", "version": "1.0.0"}
