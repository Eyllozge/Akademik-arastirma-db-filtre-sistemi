from fastapi import FastAPI
from database import SessionLocal
from models import articles

app = FastAPI()

@app.get("/")
def read_root():
    return {"mesaj": "çalışıyor"}

@app.get("/makaleler")
def get_articles():
    db = SessionLocal()
    try:
        result = db.query(articles).limit(10).all()
        return [{"art_id": a.art_id, "title": a.article_name} for a in result]
    finally:
        db.close()