from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import get_current_user
from routers import audit, history, users

app = FastAPI(title="NSU Audit Core API v2", version="2.0")

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


app.include_router(audit.router)
app.include_router(history.router)
app.include_router(users.router)


@app.get("/api/v1/me")
async def get_me(current_user=Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }
