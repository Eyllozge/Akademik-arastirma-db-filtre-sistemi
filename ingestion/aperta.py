import requests
import uuid
import hashlib
from database import SessionLocal
from models import articles, members, authors, institutions, middle

if __name__ == "__main__":
 url = "https://aperta.ulakbim.gov.tr/api/records"
 params = {
    "q": "yapay zeka",
    "size": 5
}

    
 response = requests.get(url, params=params)
 data = response.json()
 
total_records = data.get("total", 0)
print(f"HTTP Durum Kodu: {response.status_code}")
print(f"Toplam kayıt sayısı: {total_records}")



