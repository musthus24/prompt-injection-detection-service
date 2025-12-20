from fastapi import FastAPI
from app.api.routes import router as scan_router


app = FastAPI(title="Prompt Injection Detection Service", version="0.1.0")
app.include_router(scan_router)


@app.get("/health")
def health():
    return {"status": "ok"}
