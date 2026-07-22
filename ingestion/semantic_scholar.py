import requests
from database import SessionLocal
from models import articles, members, authors, institutions, middle
import uuid

url = "https://api.semanticscholar.org/graph/v1/paper/search"
params = {
    "query": "yapay zeka",
    "fields": "title,year,authors,externalIds",
    "limit": 5
}

response = requests.get(url, params=params)
data = response.json()

def parse_paper(paper):
    return {
        "art_id": paper.get("externalIds", {}).get("CorpusId"),
        "title": paper.get("title"),
        "year": paper.get("year"),
        "authors": [{"name": a["name"], "institution": None} for a in paper.get("authors", [])]
    }



for paper in data.get("data", []):
    print(parse_paper(paper))
    print(paper)
    
def save_to_db(parsed_list):
    db = SessionLocal()
    try:
        for item in parsed_list:
            db_article = articles(art_id=item["art_id"], article_name=item["title"], upload_date=None)
            db.merge(db_article)

            for author_info in item["authors"]:
                inst_name = author_info["institution"]
                db_inst = None
                if inst_name:
                    db_inst = db.query(institutions).filter_by(inst_name=inst_name).first()
                    if not db_inst:
                        db_inst = institutions(inst_name=inst_name)
                        db.add(db_inst)
                        db.flush()

                db_author = db.query(authors).filter_by(first_name=author_info["name"]).first()
                if not db_author:
                    
                    placeholder_email = f"scraped_{uuid.uuid4().hex[:8]}@placeholder.local"
                    db_member = members(
                        email=placeholder_email,
                        username=placeholder_email,
                        password="",      
                        first_name=author_info["name"],
                        last_name=""
                    )
                    db.add(db_member)
                    db.flush()  

                    db_author = authors(
                        first_name=author_info["name"],
                        last_name="",
                        institution_id=db_inst.inst_id if db_inst else None,
                        uye_id=db_member.mem_id
                    )
                    db.add(db_author)
                    db.flush()

                db.add(middle(art_id=item["art_id"], auth_id=db_author.auth_id))

        db.commit()
        print("Kayıt başarılı!")
    except Exception as e:
        db.rollback()
        print("Hata:", e)
    finally:
        db.close()
        
print(response.status_code)
print(data)
parsed_list = [parse_paper(p) for p in data.get("data", [])]
save_to_db(parsed_list)
