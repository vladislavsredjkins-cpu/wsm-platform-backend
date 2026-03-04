from fastapi import FastAPI

app = FastAPI(
    title="World Strongman Platform API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "WSM Platform API running"}

@app.get("/health")
def health():
    return {"status": "ok"}
