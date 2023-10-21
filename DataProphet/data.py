import mysql.connector

# MySQL bağlantısı oluşturma
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="101m"
)

# Veritabanı işlemleri için cursor oluşturma
cursor = db.cursor()

# Kullanıcıdan sorgu koşullarını girmesini iste
tc = input("TC girin: ")
adi = input("Adı girin: ")
soyadi = input("Soyadı girin: ")
dogum_tarihi = input("Doğum Tarihini girin (G-A-YYYY): ")
nufus_il = input("Nüfus İlini girin: ")
nufus_ilce = input("Nüfus İlçesini girin: ")
anne_adi = input("Anne Adını girin: ")
anne_tc = input("Anne TC'sini girin: ")
baba_adi = input("Baba Adını girin: ")
baba_tc = input("Baba TC'sini girin: ")
uyruk = input("Uyruğu girin: ")

# Sorguyu hazırlama
query = "SELECT * FROM `101m` WHERE"
params = []

if tc:
    params.append(f" TC='{tc}'")
if adi:
    params.append(f" ADI='{adi}'")
if soyadi:
    params.append(f" SOYADI='{soyadi}'")
if dogum_tarihi:
    params.append(f" DOGUMTARIHI='{dogum_tarihi}'")
if nufus_il:
    params.append(f" NUFUSIL='{nufus_il}'")
if nufus_ilce:
    params.append(f" NUFUSILCE='{nufus_ilce}'")
if anne_adi:
    params.append(f" ANNEADI='{anne_adi}'")
if anne_tc:
    params.append(f" ANNETC='{anne_tc}'")
if baba_adi:
    params.append(f" BABAADI='{baba_adi}'")
if baba_tc:
    params.append(f" BABATC='{baba_tc}'")
if uyruk:
    params.append(f" UYRUK='{uyruk}'")

query += " AND".join(params) + ";"

# Sorguyu çalıştırma
cursor.execute(query)

# Sorgu sonuçlarını bir metin dosyasına yazma
with open("sonuclar.txt", "w") as dosya:
    for row in cursor.fetchall():
        satir = "\t".join(str(value) for value in row)  # Sütunları sekmeyle ayırarak birleştirme
        dosya.write(satir + "\n")  # Her satırı dosyaya yazma

# Bağlantıyı kapatma
cursor.close()
db.close()