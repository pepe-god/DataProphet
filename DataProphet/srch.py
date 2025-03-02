#!/usr/bin/env python3
import mysql.connector.pooling
import csv
import logging
import time
import configparser
import tkinter as tk
from tkinter import messagebox
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import os
from typing import Dict, Tuple, Optional

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Database Configuration
DB_CONFIG: Optional[configparser.SectionProxy] = None
DB_POOL: Optional[mysql.connector.pooling.MySQLConnectionPool] = None
DB_FIELDS = {
    "TC": "TC", "Adı": "AD", "Soyadı": "SOYAD", "GSM": "GSM",
    "Baba Adı": "BABAADI", "Baba TC'si": "BABATC",
    "Anne Adı": "ANNEADI", "Anne TC'si": "ANNETC",
    "Doğum Tarihi": "DOGUMTARIHI", "Ölüm Tarihi": "OLUMTARIHI",
    "Doğum Yeri": "DOGUMYERI", "Memleket İli": "MEMLEKETIL",
    "Memleket İlçesi": "MEMLEKETILCE", "Memleket Köyü": "MEMLEKETKOY",
    "Adres İli": "ADRESIL", "Adres İlçesi": "ADRESILCE",
    "Aile Sıra No": "AILESIRANO", "Birey Sıra No": "BIREYSIRANO",
    "Medeni Hal": "MEDENIHAL", "Cinsiyet": "CINSIYET"
}

executor = ThreadPoolExecutor(max_workers=4)

def initialize_db_pool():
    global DB_CONFIG, DB_POOL
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        DB_CONFIG = config['FULLDATA']
        DB_POOL = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=8,
            pool_reset_session=True,
            **DB_CONFIG
        )
        logging.info("Database pool initialized successfully")
    except Exception as e:
        logging.critical(f"Database pool initialization failed: {e}")
        raise RuntimeError("Database connection failed") from e

@contextmanager
def db_connection():
    conn = None
    try:
        conn = DB_POOL.get_connection()
        yield conn
    except mysql.connector.Error as e:
        logging.error(f"Database error: {e}")
        messagebox.showerror("Database Error", f"{e.msg}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()

def validate_tc(tc: str) -> bool:
    return tc.isdigit() and len(tc) == 11

def build_query(conditions: Dict[str, str]) -> Tuple[str, Tuple]:
    clauses = []
    params = []
    for field, value in conditions.items():
        if not value:
            continue

        if field == "DOGUMTARIHI":
            if value.isdigit() and len(value) == 4:
                clauses.append("LEFT(DOGUMTARIHI, 4) = %s")
            else:
                clauses.append("DOGUMTARIHI LIKE %s")
                value = f"%{value}%"
        else:
            clauses.append(f"{field} = %s")

        params.append(value)

    return " AND ".join(clauses) or "1=1", tuple(params)

def execute_query(cursor, query: str, params: Tuple) -> Optional[mysql.connector.cursor.MySQLCursor]:
    try:
        start_time = time.monotonic()
        cursor.execute(query, params)
        logging.info(f"Query executed in {time.monotonic() - start_time:.3f}s")
        return cursor
    except mysql.connector.Error as e:
        logging.error(f"Query failed: {e}")
        messagebox.showerror("Query Error", f"Execution failed: {e.msg}")
        return None

def save_to_csv(filename: str, cursor, query_condition: str) -> Tuple[int, float]:
    start_time = time.monotonic()
    record_count = 0

    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(DB_FIELDS.keys())

            while True:
                rows = cursor.fetchmany(5000)
                if not rows:
                    break

                writer.writerows(rows)
                record_count += len(rows)
                logging.info(f"Written {record_count} records...")

        duration = time.monotonic() - start_time

        with open(filename, 'a', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows([
                [],
                ["Query Conditions", query_condition],
                ["Total Time (s)", f"{duration:.2f}"],
                ["Total Records", record_count]
            ])

        return record_count, duration

    except Exception as e:
        logging.error(f"CSV save failed: {e}")
        raise

def search(entries: Dict[str, tk.Entry]):
    def run_search():
        try:
            conditions = {DB_FIELDS[k]: v.get().strip() for k, v in entries.items() if v.get().strip()}

            if "TC" in conditions and not validate_tc(conditions["TC"]):
                messagebox.showwarning("Invalid Input", "Geçersiz TC Kimlik Numarası")
                return

            query_condition, params = build_query(conditions)
            query = f"SELECT {', '.join(DB_FIELDS.values())} FROM `109m` WHERE {query_condition}"
            logging.debug(f"Executing query: {query}")

            with db_connection() as conn:
                cursor = conn.cursor()
                if not execute_query(cursor, query, params):
                    return

                filename = os.path.join("./index", f"search_{time.strftime('%Y%m%d-%H%M%S')}.csv")
                record_count, duration = save_to_csv(filename, cursor, query_condition)

                messagebox.showinfo(
                    "Search Complete",
                    f"{record_count} kayıt bulundu\n"
                    f"Süre: {duration:.2f}s\n"
                    f"Dosya: {os.path.basename(filename)}"
                )

        except Exception as e:
            logging.error(f"Search failed: {e}")
            messagebox.showerror("Error", f"Arama başarısız: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            status_var.set("Ready")

    status_var.set("Arama yapılıyor...")
    executor.submit(run_search)

def create_gui():
    root = tk.Tk()
    root.title("Searcher")
    root.geometry("680x600")

    main_frame = tk.Frame(root, padx=15, pady=15)
    main_frame.pack(expand=True, fill=tk.BOTH)

    entries = {}
    for idx, field in enumerate(DB_FIELDS):
        row = idx // 2
        col = idx % 2

        frame = tk.Frame(main_frame)
        frame.grid(row=row, column=col, sticky='ew', padx=5, pady=3)

        lbl = tk.Label(frame, text=f"{field}:", width=14, anchor='w')
        lbl.pack(side=tk.LEFT)

        entry = tk.Entry(frame, width=18)
        entry.pack(side=tk.RIGHT)
        entries[field] = entry

        main_frame.columnconfigure(col, weight=1)

    global status_var
    status_var = tk.StringVar()
    status_label = tk.Label(
        root,
        textvariable=status_var,
        bd=1,
        relief=tk.SUNKEN,
        anchor=tk.W,
        bg='#f0f0f0',
        font=('Helvetica', 9)
    )
    status_label.pack(side=tk.BOTTOM, fill=tk.X)
    status_var.set("Hazır")

    search_btn = tk.Button(
        main_frame,
        text="ARA",
        command=lambda: search(entries),
        bg='#4CAF50',
        fg='white',
        activebackground='#45a049',
        height=2,
        width=20,
        font=('Helvetica', 10, 'bold')
    )
    search_btn.grid(row=len(DB_FIELDS)//2+1, column=0, columnspan=2, pady=15)

    root.mainloop()

if __name__ == "__main__":
    try:
        initialize_db_pool()
        create_gui()
    except Exception as e:
        logging.critical(f"Uygulama başlatılamadı: {e}")
        messagebox.showerror("Kritik Hata", f"Uygulama başlatılamadı:\n{str(e)}")
