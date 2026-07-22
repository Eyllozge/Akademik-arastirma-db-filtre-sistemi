import requests
import xml.etree.ElementTree as ET
from database import SessionLocal
from models import articles, members, authors, institutions, middle
import uuid


url = "https://dergipark.org.tr/api/public/oai/"
params = {
    "verb": "ListRecords",
    "metadataPrefix": "oai_dc",
    "set": "auhfd"   
}

response = requests.get(url, params=params)
print(response.status_code)
print(response.text[:2000])

def parse_dergipark_xml(xml_text):
    ns = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/'
    }
    root = ET.fromstring(xml_text)
    records = []
    for record in root.findall('.//oai:record', ns):
        metadata = record.find('.//oai_dc:dc', ns)
        if metadata is None:
            continue
        title_el = metadata.find('dc:title[@{http://www.w3.org/XML/1998/namespace}lang="tr-TR"]', ns)
        title = title_el.text.strip() if title_el is not None else None
        creators = [c.text.strip() for c in metadata.findall('dc:creator', ns)]
        identifier = record.find('.//oai:identifier', ns).text

        records.append({
            "art_id": abs(hash(identifier)) % (10**8), 
            "title": title,
            "year": None,
            "authors": [{"name": c, "institution": None} for c in creators]
        })
    return records

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
        
parsed_list = parse_dergipark_xml(response.text)
for r in parsed_list:
    print(r)

save_to_db(parsed_list)