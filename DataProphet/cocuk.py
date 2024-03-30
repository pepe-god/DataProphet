from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Veritabanı bağlantısı oluşturma
engine = create_engine('mysql+mysqlconnector://root:@localhost/101m')
Session = sessionmaker(bind=engine)
session = Session()

# Tabloyu temsil edecek model sınıfını oluşturma
Base = declarative_base()

class Person(Base):
    __tablename__ = '101m'
    id = Column(Integer, primary_key=True)
    TC = Column(String)
    ADI = Column(String)
    SOYADI = Column(String)
    DOGUMTARIHI = Column(String)
    NUFUSIL = Column(String)
    NUFUSILCE = Column(String)
    ANNEADI = Column(String)
    ANNETC = Column(String)
    BABAADI = Column(String)
    BABATC = Column(String)
    UYRUK = Column(String)

# Anne ve baba TC numaralarını belirleme
anne_tc = "12345678912"
baba_tc = "12345678912"

# Anne'nin çocuklarını sorgulama
anne_cocuklar = session.query(Person).filter(Person.ANNETC == anne_tc).all()

# Baba'nın çocuklarını sorgulama
baba_cocuklar = session.query(Person).filter(Person.BABATC == baba_tc).all()

# Çocukları cocuk.txt dosyasına kaydetme
with open("cocuk.txt", "w") as dosya:
    dosya.write(f"Annemin çocukları (TC: {anne_tc}):\n\n")
    for cocuk in anne_cocuklar:
        dosya.write(f"{cocuk.TC} - {cocuk.ADI} {cocuk.SOYADI}\n")

    dosya.write(f"\nBabanın çocukları (TC: {baba_tc}):\n\n")
    for cocuk in baba_cocuklar:
        dosya.write(f"{cocuk.TC} - {cocuk.ADI} {cocuk.SOYADI}\n")

print("Çocuklar başarıyla kaydedildi.")

# Veritabanı bağlantısını kapatma
session.close()