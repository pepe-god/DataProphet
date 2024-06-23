import mysql.connector
import csv

def get_user_input(field_name):
    return input(f"{field_name} girin: ")

def build_query(**kwargs):
    conditions = [f"{field}='{value}'" for field, value in kwargs.items() if value]
    return " AND ".join(conditions)

def write_person_info(writer, person):
    writer.writerow(person[1:])

# MySQL bağlantısı oluşturma
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="101m"
)

# Veritabanı işlemleri için cursor oluşturma
cursor = db.cursor()

# Kullanıcıdan sorgu koşullarını al
query_conditions = {
    "TC": get_user_input("TC"),
    "ADI": get_user_input("Adı"),
    "SOYADI": get_user_input("Soyadı"),
    "DOGUMTARIHI": get_user_input("Doğum Tarihi (G-A-YYYY)"),
    "NUFUSIL": get_user_input("Nüfus İli"),
    "NUFUSILCE": get_user_input("Nüfus İlçesi"),
    "ANNEADI": get_user_input("Anne Adı"),
    "ANNETC": get_user_input("Anne TC'si"),
    "BABAADI": get_user_input("Baba Adı"),
    "BABATC": get_user_input("Baba TC'si"),
    "UYRUK": get_user_input("Uyruk")
}

# Sorguyu hazırla ve çalıştır
query = "SELECT * FROM `101m` WHERE " + build_query(**query_conditions)
cursor.execute(query)

# Sonuçları dosyaya yaz
with open("searcher.csv", "w", encoding="utf-8", newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["TC", "Adı", "Soyadı", "Doğum Tarihi", "Nüfus İli", "Nüfus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk"])
    for row in cursor.fetchall():
        write_person_info(writer, row)

# Bağlantıyı kapat
cursor.close()
db.close()
