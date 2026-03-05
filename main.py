from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vladislavredjkins-cpu.github.io",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app = FastAPI(title="World Strongman Platform API", version="1.0.0")

# CORS — чтобы Swagger UI на GitHub Pages мог вызывать Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vladislavsvredjkins-cpu.github.io",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/__build")
def __build():
    return {"service": "wsm-platform-backend", "build": "RANKING_V1"}

@app.get("/ranking")
def get_ranking(
    division: str = Query("MEN"),
    format: str = Query("CLASSIC"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return {
        "division": division,
        "format": format,
        "limit": limit,
        "offset": offset,
        "items": [],
    }
