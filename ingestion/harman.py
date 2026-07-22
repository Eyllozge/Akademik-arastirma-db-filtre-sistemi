import requests
import uuid
import hashlib
from database import SessionLocal
from models import articles, members, authors, institutions, middle


def generate_stable_id(string_id):
    return int(hashlib.sha256(string_id.encode('utf-8')).hexdigest(), 16) % (10**8)

def parse_harman(pub): #ham veriyi çeviren fonksiyon
    source = pub.get("_source", {})
    metadata = source.get("metadata", {})
    
    title = metadata.get("primary_title", "Bilinmeyen Başlık")
    year = metadata.get("publication_year")
    creators = metadata.get("creator", [])

    return {
        "art_id": generate_stable_id(pub["_id"]), 
        "title": title,
        "year": year,
        "authors": [{"name": name, "institution": None} for name in creators]
    }

def split_name(full_name):

    parts = full_name.strip().split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return full_name, ""

def save_to_db(parsed_list):
    db = SessionLocal()
    try:
        for item in parsed_list:
            
            db_article = articles(art_id=item["art_id"], article_name=item["title"], upload_date=None)
            db.merge(db_article)

            for author_info in item["authors"]:
                
                inst_name = author_info.get("institution")
                db_inst = None
                if inst_name:
                    db_inst = db.query(institutions).filter_by(inst_name=inst_name).first()
                    if not db_inst:
                        db_inst = institutions(inst_name=inst_name)
                        db.add(db_inst)
                        db.flush()

                first_name, last_name = split_name(author_info["name"])
                db_author = db.query(authors).filter_by(first_name=first_name, last_name=last_name).first()
                
                if not db_author:
                    placeholder_email = f"scraped_{uuid.uuid4().hex[:8]}@placeholder.local"
                    db_member = members(
                        email=placeholder_email,
                        username=placeholder_email,
                        password="",
                        first_name=first_name,
                        last_name=last_name
                    )
                    db.add(db_member)
                    db.flush()

                    db_author = authors(
                        first_name=first_name,
                        last_name=last_name,
                        institution_id=db_inst.inst_id if db_inst else None,
                        uye_id=db_member.mem_id
                    )
                    db.add(db_author)
                    db.flush() #db commit etmeden önce auth_id almak için flush kullanılıyor.

                
                existing_relation = db.query(middle).filter_by(art_id=item["art_id"], auth_id=db_author.auth_id).first()
                if not existing_relation:
                    db.add(middle(art_id=item["art_id"], auth_id=db_author.auth_id))
                 #bu üstteki existing kısmı bu makale yazar bağlantısı zaten varsa tekrar eklememek için kontrol ediyor.
        db.commit()
        print(f"Başarıyla {len(parsed_list)} kayıt işlendi!")
    except Exception as e:
        db.rollback()
        print("Veritabanı işlem hatası:", e)
    finally:
        db.close()

if __name__ == "__main__":
    url = "https://search.harman.ulakbim.gov.tr/api/defaultSearch/publication/"
    params = {
        "q": "yapay zeka",
        "order": "relevance-DESC",
        "page": 1,
        "limit": 45
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() 
        data = response.json()
        
        
        hits = data.get("hits", {}).get("hits", [])
        
        if hits:
            parsed_list = [parse_harman(pub) for pub in hits]

            save_to_db(parsed_list)
        else:
            print("API yanıtında işlenecek sonuç bulunamadı.")
            
    except requests.exceptions.RequestException as e:
        print("API isteği sırasında hata oluştu:", e)