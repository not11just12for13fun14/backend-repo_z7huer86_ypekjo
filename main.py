import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Title

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Streaming API ready"}

# Seed minimal content if collection empty (helper)
async def ensure_seed_data():
    try:
        if db is None:
            return
        count = db["title"].count_documents({})
        if count == 0:
            samples = [
                {
                    "name": "Stranger Things",
                    "type": "series",
                    "year": 2016,
                    "genres": ["Sci-Fi", "Thriller"],
                    "description": "When a young boy vanishes, a small town uncovers a mystery involving secret experiments.",
                    "poster_url": "https://image.tmdb.org/t/p/w342/x2LSRK2Cm7MZhjluni1msVJ3wDF.jpg",
                    "backdrop_url": "https://image.tmdb.org/t/p/w1280/56v2KjBlU4XaOv9rVYEQypROD7P.jpg",
                    "thumb_url": "https://image.tmdb.org/t/p/w300/49WJfeN0moxb9IPfGn8AIqMGskD.jpg",
                    "rating": 8.6,
                    "mature": False,
                },
                {
                    "name": "Extraction",
                    "type": "movie",
                    "year": 2020,
                    "genres": ["Action", "Thriller"],
                    "description": "A fearless black market mercenary embarks on the most deadly extraction of his career.",
                    "poster_url": "https://image.tmdb.org/t/p/w342/wlfDxbGEsW58vGhFljKkcR5IxDj.jpg",
                    "backdrop_url": "https://image.tmdb.org/t/p/w1280/wwF9c83TtqgkQJu1Mst7IRYpA8Y.jpg",
                    "thumb_url": "https://image.tmdb.org/t/p/w300/wlfDxbGEsW58vGhFljKkcR5IxDj.jpg",
                    "rating": 7.1,
                    "mature": True,
                },
                {
                    "name": "Wednesday",
                    "type": "series",
                    "year": 2022,
                    "genres": ["Comedy", "Mystery"],
                    "description": "Wednesday Addams investigates a murder spree while making new friends and foes at Nevermore Academy.",
                    "poster_url": "https://image.tmdb.org/t/p/w342/9PFonBhy4cQy7Jz20NpMygczOkv.jpg",
                    "backdrop_url": "https://image.tmdb.org/t/p/w1280/jeGvzg2vYqMENAqaE3ULw7qGRCF.jpg",
                    "thumb_url": "https://image.tmdb.org/t/p/w300/9PFonBhy4cQy7Jz20NpMygczOkv.jpg",
                    "rating": 8.3,
                    "mature": False,
                },
            ]
            for s in samples:
                create_document("title", s)
    except Exception:
        pass

class TitlesResponse(BaseModel):
    items: List[Title]

@app.get("/api/titles", response_model=TitlesResponse)
async def list_titles(
    q: Optional[str] = Query(None, description="Search by name"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    type: Optional[str] = Query(None, description="movie or series"),
    limit: int = Query(50, ge=1, le=100)
):
    await ensure_seed_data()

    filter_dict = {}
    if q:
        filter_dict["name"] = {"$regex": q, "$options": "i"}
    if genre:
        filter_dict["genres"] = genre
    if type:
        filter_dict["type"] = type

    try:
        docs = get_documents("title", filter_dict, limit)
        # Convert ObjectId to string-safe dicts and validate to Title model
        items: List[Title] = []
        for d in docs:
            d.pop("_id", None)
            items.append(Title(**d))
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
