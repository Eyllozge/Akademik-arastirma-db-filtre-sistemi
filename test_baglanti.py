from database import engine

try:
    connection = engine.connect()
    print("Bağlantı başarılı!")
    connection.close()
except Exception as e:
    print("Hata:", e)