#!/usr/bin/env python3
import mysql.connector
import csv
import logging
import time
import configparser
import tkinter as tk
from tkinter import messagebox

# Günlük kaydı için temel yapılandırma
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_tc(tc):
    if tc and len(tc) == 11 and tc.isdigit():
        return True
    return False

def build_query(conditions):
    query = " AND ".join(f"{field}='{value}'" if field != "DOGUMTARIHI" else f"{field} LIKE '%{value}%'" for field, value in conditions.items() if value)
    logging.debug(f"Oluşturulan Sorgu: {query}")
    return query

def write_person_info(writer, person):
    writer.writerow(person)

def connect_to_database():
    config = configparser.ConfigParser()
    config.read('config.ini')
    db_config = config['DATABASE']
    try:
        db = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
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

def search(entries):
    db = connect_to_database()
    if not db:
        messagebox.showerror("Hata", "Veritabanına bağlanılamadı.")
        return

    cursor = db.cursor()

    # Kullanıcıdan sorgu koşullarını al
    query_conditions = {
        "TC": entries["TC"].get(),
        "ADI": entries["Adı"].get(),
        "SOYADI": entries["Soyadı"].get(),
        "DOGUMTARIHI": entries["Doğum Yılı (YYYY)"].get(),  # Doğum yılı olarak alınıyor
        "NUFUSIL": entries["Nüfus İli"].get(),
        "NUFUSILCE": entries["Nüfus İlçesi"].get(),
        "ANNEADI": entries["Anne Adı"].get(),
        "ANNETC": entries["Anne TC'si"].get(),
        "BABAADI": entries["Baba Adı"].get(),
        "BABATC": entries["Baba TC'si"].get(),
        "UYRUK": entries["Uyruk"].get()
    }

    # TC doğrulama
    if query_conditions["TC"] and not validate_tc(query_conditions["TC"]):
        messagebox.showwarning("Uyarı", "Geçersiz TC kimlik numarası.")
        return

    # Sorguyu hazırla ve çalıştır
    query = "SELECT * FROM `101m` WHERE " + build_query(query_conditions)
    success, start_time, end_time, query_time = execute_query(cursor, query)
    if not success:
        cursor.close()
        db.close()
        return

    # Sonuçları al
    results = cursor.fetchall()
    total_records = len(results)

    # Sonuçları dosyaya yaz
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"searcher_{timestamp}.csv"
    with open(filename, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["TC", "Adı", "Soyadı", "Doğum Tarihi", "Nüfus İli", "Nüfus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk"])
        for row in results:
            # ID sütununu atlayarak diğer sütunları yaz
            write_person_info(writer, row[1:])

        # Sorgu bilgilerini en alt kısma yaz
        writer.writerow([])  # Boş satır ekleyelim
        writer.writerow(["Sorgu Koşulları", build_query(query_conditions)])
        writer.writerow(["İlk Sorgu Zamanı", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))])
        writer.writerow(["Son Sorgu Zamanı", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))])
        writer.writerow(["Toplam Sorgu Süresi (s)", query_time])
        writer.writerow(["Toplam Kayıt Sayısı", total_records])

    messagebox.showinfo("Bilgi", f"Sonuçlar başarıyla {filename} dosyasına yazıldı. Toplam kayıt sayısı: {total_records}")

    # Bağlantıyı kapat
    cursor.close()
    db.close()

def create_gui():
    root = tk.Tk()
    root.title("Searcher")

    entries = {}
    fields = ["TC", "Adı", "Soyadı", "Doğum Yılı (YYYY)", "Nüfus İli", "Nüfus İlçesi", "Anne Adı", "Anne TC'si", "Baba Adı", "Baba TC'si", "Uyruk"]

    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=22, text=field + ": ", anchor='w')
        ent = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries[field] = ent

    button = tk.Button(root, text="Arama Yap", command=lambda: search(entries))
    button.pack(side=tk.BOTTOM, pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
