import requests
from database import SessionLocal
from models import articles, members, authors, institutions, middle
import uuid
from bs4 import BeautifulSoup

url = "https://dblp.org/search?q=artificial%20intelligence"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")


results = soup.find_all("li", class_="entry")
print(f"{len(results)} sonuç bulundu")



def parse_dblp_results(results):
    parsed = []
    for r in results[:5]:
        title_tag = r.find("span", class_="title")
        title = title_tag.text.strip() if title_tag else None
        author_names = [a.text.strip() for a in r.find_all("span", itemprop="author")]
        year_tag = r.find("span", itemprop="datePublished")
        year = year_tag.text.strip() if year_tag else None

        parsed.append({
            "art_id": abs(hash(title)) % (10**8),
            "title": title,
            "year": year,
            "authors": [{"name": n, "institution": None} for n in author_names]
        })
    return parsed


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

parsed_list = parse_dblp_results(results)
save_to_db(parsed_list) 