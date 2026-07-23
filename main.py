from fastapi import FastAPI
from database import SessionLocal
from models import articles, middle , authors, institutions

app = FastAPI()

@app.get("/")
def read_root():
    return {"çalışıyor"}

@app.get("/makaleler")
def get_articles():
    db = SessionLocal()
    try:
        result = db.query(articles).limit(10).all()
        return [{"art_id": a.art_id, "title": a.article_name} for a in result]
    finally:
        db.close()

@app.get("/makaleler/ara")
def search_articles(q: str):
    db = SessionLocal()
    try:
        result = db.query(articles).filter(articles.article_name.ilike(f"%{q}%")).limit(20).all()
        return [{"art_id": a.art_id, "title": a.article_name} for a in result]
    finally:
        db.close()

@app.get("/yazarlar/ara")
def search_by_author(name: str):
    db = SessionLocal()
    try:
        result = (
            db.query(articles)
            .join(middle, middle.art_id == articles.art_id)
            .join(authors, authors.auth_id == middle.auth_id)
            .filter(authors.first_name.ilike(f"%{name}%"))
            .limit(20)
            .all()
        )
        return [{"art_id": a.art_id, "title": a.article_name} for a in result]
    finally:
        db.close()
        

@app.get("/kurumlar/ara")
def search_by_institution(name: str):
    db = SessionLocal()
    try:
        result = (
            db.query(articles)
            .join(middle, middle.art_id == articles.art_id)
            .join(authors, authors.auth_id == middle.auth_id)
            .join(institutions, institutions.inst_id == authors.institution_id)
            .filter(institutions.inst_name.ilike(f"%{name}%"))
            .limit(20)
            .all()
        )
        return [{"art_id": a.art_id, "title": a.article_name} for a in result]
    finally:
        db.close()


@app.get("/makaleler/tarih")
def search_by_year_range(start: int, end: int):
    db = SessionLocal()
    try:
        result = (
            db.query(articles)
            .filter(articles.upload_date.between(f"{start}-01-01", f"{end}-12-31"))
            .limit(20)
            .all()
        )
        return [{"art_id": a.art_id, "title": a.article_name} for a in result]
    finally:
        db.close()