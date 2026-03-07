from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from routers import audit, history, users

app = FastAPI(
    title="NSU Audit Core API v2",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Starting NSU Audit Core API v2")
    print("API docs available at /docs")

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0"}

# app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])
# app.include_router(history.router, prefix="/api/v1/history", tags=["History"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
