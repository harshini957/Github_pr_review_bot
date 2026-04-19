from fastapi import FastAPI
from app.api.webhook import router
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="PR Review Bot")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}