import requests
from database import SessionLocal
from models import articles, members, authors, institutions, middle
import uuid

url = "https://search.trdizin.gov.tr/api/defaultSearch/publication/"
params = {
    "q": "yapay zeka",
    "order": "relevance-DESC",
    "page": 1,
    "limit": 5
}

response = requests.get(url, params=params)
data = response.json()

def parse_publication(pub):
    source = pub["_source"]
    art_id = source["id"]
    title = source["abstracts"][0]["title"] if source.get("abstracts") else None
    year = source.get("publicationYear")

    authors = []
    for a in source.get("authors", []):
        authors.append({
            "name": a.get("name"),
            "institution": a.get("institution", {}).get("fullTitle", [None])[0]
        })

    citations = []
    for ref in source.get("references", []):
        if ref.get("targetPublication", 0) != 0:
            citations.append(ref["targetPublication"])

    return {"art_id": art_id, "title": title, "year": year, "authors": authors, "citations": citations}


    
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
                    # önce boş/placeholder üye kaydı aç
                    placeholder_email = f"scraped_{uuid.uuid4().hex[:8]}@placeholder.local"
                    db_member = members(
                        email=placeholder_email,
                        username=placeholder_email,
                        password="",       # gerçek şifresi yok, boş bırakılıyor
                        first_name=author_info["name"],
                        last_name=""
                    )
                    db.add(db_member)
                    db.flush()   # mem_id'sini almak için

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


parsed_list = [parse_publication(pub) for pub in data["hits"]["hits"]]
save_to_db(parsed_list)