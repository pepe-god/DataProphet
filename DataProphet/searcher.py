import mysql.connector
import csv
import logging
import time
import re

# Günlük kaydı için temel yapılandırma
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_tc(tc):
    if tc and len(tc) == 11 and tc.isdigit():
        return True
    return False

def get_user_input(field_name):
    while True:
        value = input(f"{field_name} girin: ").strip() or None
        if field_name == "TC" and value:
            if not validate_tc(value):
                logging.warning("Geçersiz TC kimlik numarası. Lütfen tekrar deneyin.")
                continue
        logging.debug(f"{field_name}: {value}")
        return value

def build_query(conditions):
    query = " AND ".join(f"{field}='{value}'" for field, value in conditions.items() if value)
    logging.debug(f"Oluşturulan Sorgu: {query}")
    return query

def write_person_info(writer, person):
    writer.writerow(person)

def connect_to_database():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="101m"
        )
        logging.info("Veritabanı bağlantısı başarılı.")
        return db
    except mysql.connector.Error as err:
        logging.error(f"Veritabanı bağlantı hatası: {err}")
        return None

def execute_query(cursor, query):
    try:
        start_time = time.time()
        cursor.execute(query)
        end_time = time.time()
        logging.info("Sorgu başarıyla çalıştırıldı.")
        return True, start_time, end_time, end_time - start_time
    except mysql.connector.Error as err:
        logging.error(f"Sorgu hatası: {err}")
        return False, 0, 0, 0

def main():
    db = connect_to_database()
    if not db:
        return

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
    query = "SELECT * FROM `101m` WHERE " + build_query(query_conditions)
    success, start_time, end_time, query_time = execute_query(cursor, query)
    if not success:
        cursor.close()
        db.close()
        return

    # Sonuçları dosyaya yaz
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"searcher_{timestamp}.csv"
    with open(filename, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["TC", "Adı", "Soyadı", "Doğum Tarihi", "Nüfus İli", "Nüfus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk"])
        for row in cursor.fetchall():
            # ID sütununu atlayarak diğer sütunları yaz
            write_person_info(writer, row[1:])

        # Sorgu bilgilerini en alt kısma yaz
        writer.writerow([])  # Boş satır ekleyelim
        writer.writerow(["Sorgu Koşulları", build_query(query_conditions)])
        writer.writerow(["İlk Sorgu Zamanı", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))])
        writer.writerow(["Son Sorgu Zamanı", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))])
        writer.writerow(["Toplam Sorgu Süresi (s)", query_time])

    logging.info(f"Sonuçlar başarıyla {filename} dosyasına yazıldı.")

    # Bağlantıyı kapat
    cursor.close()
    db.close()

if __name__ == "__main__":
    main()
