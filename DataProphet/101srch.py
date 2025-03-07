#!/usr/bin/env python3
import mysql.connector
import csv
import logging
import time
import configparser
import tkinter as tk
from tkinter import messagebox

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_tc(tc): return tc and len(tc) == 11 and tc.isdigit()

def build_query(conditions): return " AND ".join(f"{field}='{value}'" if field != "DOGUMTARIHI" else f"{field} LIKE '%{value}%'" for field, value in conditions.items() if value)

def connect_to_database():
    config = configparser.ConfigParser()
    config.read('config.ini')
    db_config = config['DATABASE']
    try:
        db = mysql.connector.connect(**db_config)
        logging.info("Veritabanı bağlantısı başarılı.")
        return db
    except mysql.connector.Error as err:
        logging.error(f"Veritabanı bağlantı hatası: {err}")
        return None

def execute_query(cursor, query, limit=None, offset=None):
    try:
        if limit: query += f" LIMIT {limit}"
        if offset: query += f" OFFSET {offset}"
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
    query_conditions = {field: entries[field].get() for field in ["TC", "Adı", "Soyadı", "Doğum Yılı (YYYY)", "Nüfus İli", "Nüfus İlçesi", "Anne Adı", "Anne TC'si", "Baba Adı", "Baba TC'si", "Uyruk"]}

    if query_conditions["TC"] and not validate_tc(query_conditions["TC"]):
        messagebox.showwarning("Uyarı", "Geçersiz TC kimlik numarası.")
        return

    db_fields = {
        "TC": "TC", "Adı": "ADI", "Soyadı": "SOYADI", "Doğum Yılı (YYYY)": "DOGUMTARIHI",
        "Nüfus İli": "NUFUSIL", "Nüfus İlçesi": "NUFUSILCE", "Anne Adı": "ANNEADI", "Anne TC'si": "ANNETC",
        "Baba Adı": "BABAADI", "Baba TC'si": "BABATC", "Uyruk": "UYRUK"
    }

    query_conditions = {db_fields[field]: value for field, value in query_conditions.items()}
    query = "SELECT * FROM `101m` WHERE " + build_query(query_conditions)
    limit, offset, total_records = 100000, 0, 0
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"./index/searcher_{timestamp}.csv"

    with open(filename, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["TC", "Adı", "Soyadı", "Doğum Tarihi", "Nüfus İli", "Nüfus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk"])

        while True:
            success, start_time, end_time, query_time = execute_query(cursor, query, limit, offset)
            if not success: break

            results = cursor.fetchall()
            if not results: break

            for row in results:
                writer.writerow(row[1:])
                total_records += 1

            offset += limit

        writer.writerow([]); writer.writerow(["Sorgu Koşulları", build_query(query_conditions)])
        writer.writerow(["İlk Sorgu Zamanı", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))])
        writer.writerow(["Son Sorgu Zamanı", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))])
        writer.writerow(["Toplam Sorgu Süresi (s)", query_time])
        writer.writerow(["Toplam Kayıt Sayısı", total_records])

    messagebox.showinfo("Bilgi", f"Sonuçlar başarıyla {filename} dosyasına yazıldı. Toplam kayıt sayısı: {total_records}")
    cursor.close(); db.close()

def create_gui():
    root = tk.Tk(); root.title("Searcher")
    entries = {}
    fields = ["TC", "Adı", "Soyadı", "Doğum Yılı (YYYY)", "Nüfus İli", "Nüfus İlçesi", "Anne Adı", "Anne TC'si", "Baba Adı", "Baba TC'si", "Uyruk"]

    for field in fields:
        row = tk.Frame(root)
        tk.Label(row, width=22, text=field + ": ", anchor='w').pack(side=tk.LEFT)
        ent = tk.Entry(row)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        entries[field] = ent

    tk.Button(root, text="Arama Yap", command=lambda: search(entries)).pack(side=tk.BOTTOM, pady=20)
    root.mainloop()

if __name__ == "__main__":
    create_gui()
