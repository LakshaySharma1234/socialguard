from fastapi import FastAPI
from app.api.routes import router
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SocialGuard API",
    description="AI Comment Spam Detection API",
    version="1.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "SocialGuard backend running"}