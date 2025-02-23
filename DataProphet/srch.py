#!/usr/bin/env python3
import mysql.connector, csv, logging, time, configparser, tkinter as tk
from tkinter import messagebox
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_FIELDS = {
    "TC": "TC", "Adı": "AD", "Soyadı": "SOYAD", "GSM": "GSM", "Baba Adı": "BABAADI", "Baba TC'si": "BABATC",
    "Anne Adı": "ANNEADI", "Anne TC'si": "ANNETC", "Doğum Tarihi": "DOGUMTARIHI", "Ölüm Tarihi": "OLUMTARIHI",
    "Doğum Yeri": "DOGUMYERI", "Memleket İli": "MEMLEKETIL", "Memleket İlçesi": "MEMLEKETILCE",
    "Memleket Köyü": "MEMLEKETKOY", "Adres İli": "ADRESIL", "Adres İlçesi": "ADRESILCE",
    "Aile Sıra No": "AILESIRANO", "Birey Sıra No": "BIREYSIRANO", "Medeni Hal": "MEDENIHAL", "Cinsiyet": "CINSIYET"
}

validate_tc = lambda tc: tc.isdigit() and len(tc) == 11 if tc else False
build_query = lambda conds: " AND ".join(
    f"{k} LIKE '%{v}%'" if k == "DOGUMTARIHI" else f"{k}='{v}'"
    for k, v in conds.items() if v
)

@contextmanager
def db_connection():
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        with mysql.connector.connect(**config['FULLDATA']) as conn:
            yield conn
    except Exception as e:
        messagebox.showerror("Hata", f"DB Bağlantı Hatası: {e}")
        yield None

def execute_query(cursor, query, limit=10**5, offset=0):
    try:
        cursor.execute(f"{query} LIMIT {limit} OFFSET {offset}")
        return cursor.fetchall()
    except Exception as e:
        logging.error(f"Sorgu Hatası: {e}")
        return []

def search(entries):
    with db_connection() as db:
        if not db: return

        q_conds = {DB_FIELDS[k]: v.get() for k, v in entries.items() if v.get()}
        if entries["TC"].get() and not validate_tc(entries["TC"].get()):
            return messagebox.showwarning("Uyarı", "Geçersiz TC")

        query = f"SELECT {', '.join(DB_FIELDS.values())} FROM `109m` WHERE " + (
            build_query(q_conds) if q_conds else "1=1"
        )
        filename = f"./index/searcher_{time.strftime('%Y%m%d-%H%M%S')}.csv"
        start_time = time.time()

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(DB_FIELDS.keys())
            total = 0
            offset = 0

            while True:
                results = execute_query(db.cursor(), query, limit=10**5, offset=offset)
                if not results: break

                writer.writerows(results)
                total += len(results)
                offset += 10**5

            meta = [
                [], ["Sorgu Koşulları", build_query(q_conds)],
                ["Toplam Süre (s)", round(time.time() - start_time, 2)],
                ["Toplam Kayıt", total]
            ]
            writer.writerows(meta)

        messagebox.showinfo("Bilgi", f"{filename} oluşturuldu\nKayıt: {total}")

def create_gui():
    root = tk.Tk()
    root.title("Searcher")
    entries = {}

    for field in DB_FIELDS:
        frame = tk.Frame(root)
        tk.Label(frame, width=15, text=f"{field}:", anchor='w').pack(side=tk.LEFT)
        entries[field] = tk.Entry(frame)
        entries[field].pack(side=tk.RIGHT, expand=True, fill=tk.X)
        frame.pack(fill=tk.X, padx=3, pady=3)

    tk.Button(root, text="Arama Yap", command=lambda: search(entries)).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    create_gui()
