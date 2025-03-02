#!/usr/bin/env python3
import configparser
import csv
import logging
import re
import time
import mysql.connector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_FIELDS = [
    "TC", "AD", "SOYAD", "GSM", "BABAADI", "BABATC", "ANNEADI", "ANNETC", "DOGUMTARIHI", "OLUMTARIHI",
    "DOGUMYERI", "MEMLEKETIL", "MEMLEKETILCE", "MEMLEKETKOY", "ADRESIL", "ADRESILCE", "AILESIRANO",
    "BIREYSIRANO", "MEDENIHAL", "CINSIYET"
]
CSV_HEADER = [
    "Kategori", "TC", "AD", "SOYAD", "GSM", "DOGUMTARIHI", "OLUMTARIHI", "DOGUMYERI", "MEMLEKETIL",
    "MEMLEKETILCE", "MEMLEKETKOY", "ADRESIL", "ADRESILCE", "GUNCELADRES", "MEDENIHAL", "CINSIYET",
    "AILESIRANO", "BIREYSIRANO"
]
RELATION_CATEGORIES = ["Ana Kayıt", "Anne", "Baba", "Anneanne", "Dede(Anne)", "Babaanne", "Dede(Baba)"]
SIBLING_CATEGORIES = ["Erkek Kardeş", "Kız Kardeş"]
CHILD_CATEGORIES = ["Oğlu", "Kızı"]
UNCLE_AUNT_CATEGORIES = ["Amca", "Hala", "Dayı", "Teyze"]
COUSIN_CATEGORIES = ["Kuzen"]
NIECE_NEPHEW_CATEGORIES = ["Yeğen"]

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['FULLDATA'], config['ADRESSDATA']

def validate_tc(tc_no):
    return len(tc_no) == 11 and tc_no.isdigit()

def connect_to_database(db_config, db_name):
    try:
        logging.debug(f"Connecting to {db_name} database...")
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(buffered=True)
        logging.debug(f"Successfully connected to {db_name} database.")
        return connection
    except mysql.connector.Error as e:
        logging.error(f"Database connection error for {db_name}: {e}")
        return None

def fetch_person_by_tc(cursor, tc_no):
    try:
        cursor.execute("SELECT " + ", ".join(DB_FIELDS) + " FROM `109m` WHERE TC = %s", (tc_no,))
        person_data = cursor.fetchone()
        if person_data:
            return dict(zip(DB_FIELDS, person_data))
        return None
    except mysql.connector.Error as e:
        logging.error(f"Error fetching person with TC {tc_no}: {e}")
        return None

def fetch_relatives_by_criteria(cursor, criteria, params):
    try:
        query = "SELECT " + ", ".join(DB_FIELDS) + " FROM `109m` WHERE " + criteria
        cursor.execute(query, params)
        relative_data = cursor.fetchall()  # Tüm sonuçları hemen oku
        return [dict(zip(DB_FIELDS, person)) for person in relative_data]
    except mysql.connector.Error as e:
        logging.error(f"Error fetching relatives with criteria '{criteria}': {e}")
        return []

def fetch_address(cursor_address_local, tc_no):
    try:
        cursor_address_local.execute("SELECT GUNCELADRES FROM adresv2 WHERE TC = %s", (tc_no,))
        result = cursor_address_local.fetchone()
        return result[0] if result else ""
    except mysql.connector.Error as e:
        logging.error(f"Address fetching error for TC {tc_no}: {e}")
        return ""

def clean_address(address):
    if not address:
        return ""
    return re.sub(r'\s+\S+\s+\S+\s+\S+$', '', address).strip()

def write_person_info_to_csv(writer, person_dict, category, cursor_address_local):
    if not person_dict:
        return

    address = fetch_address(cursor_address_local, person_dict['TC'])
    cleaned_address = clean_address(address)

    row = [
        category,
        person_dict.get('TC', ''),
        person_dict.get('AD', ''),
        person_dict.get('SOYAD', ''),
        person_dict.get('GSM', ''),
        person_dict.get('DOGUMTARIHI', ''),
        person_dict.get('OLUMTARIHI', ''),
        person_dict.get('DOGUMYERI', ''),
        person_dict.get('MEMLEKETIL', ''),
        person_dict.get('MEMLEKETILCE', ''),
        person_dict.get('MEMLEKETKOY', ''),
        person_dict.get('ADRESIL', ''),
        person_dict.get('ADRESILCE', ''),
        cleaned_address,
        person_dict.get('MEDENIHAL', ''),
        person_dict.get('CINSIYET', ''),
        person_dict.get('AILESIRANO', ''),
        person_dict.get('BIREYSIRANO', '')
    ]
    writer.writerow(row)

def process_tc_number(tc_no):
    if not validate_tc(tc_no):
        return "Geçersiz TC"

    db_full_config, db_address_config = read_config()
    cnx_full = connect_to_database(db_full_config, "fulldata")
    if not cnx_full:
        return "Veritabanı hatası"

    cnx_address_local = connect_to_database(db_address_config, "address")
    if not cnx_address_local:
        return "Adres veritabanı hatası"

    try:
        with cnx_full.cursor(buffered=True) as cursor_full, cnx_address_local.cursor(buffered=True) as cursor_address_local:
            main_person_dict = fetch_person_by_tc(cursor_full, tc_no)
            if not main_person_dict:
                return "Kayıt yok"

            filename = f"./index/{main_person_dict['AD']}_{main_person_dict['SOYAD']}.csv"
            logging.info(f"Writing family information for TC: {tc_no} to file: {filename}")

            with open(filename, "w", encoding="utf-8", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(CSV_HEADER)

                relations = {
                    "Ana Kayıt": main_person_dict,
                    "Anne": fetch_person_by_tc(cursor_full, main_person_dict.get('ANNETC')) if main_person_dict.get('ANNETC') else None,
                    "Baba": fetch_person_by_tc(cursor_full, main_person_dict.get('BABATC')) if main_person_dict.get('BABATC') else None,
                    "Anneanne": fetch_person_by_tc(cursor_full, fetch_person_by_tc(cursor_full, main_person_dict.get('ANNETC')).get('ANNETC')) if main_person_dict.get('ANNETC') and fetch_person_by_tc(cursor_full, main_person_dict.get('ANNETC')) else None,
                    "Dede(Anne)": fetch_person_by_tc(cursor_full, fetch_person_by_tc(cursor_full, main_person_dict.get('ANNETC')).get('BABATC')) if main_person_dict.get('ANNETC') and fetch_person_by_tc(cursor_full, main_person_dict.get('ANNETC')) else None,
                    "Babaanne": fetch_person_by_tc(cursor_full, fetch_person_by_tc(cursor_full, main_person_dict.get('BABATC')).get('ANNETC')) if main_person_dict.get('BABATC') and fetch_person_by_tc(cursor_full, main_person_dict.get('BABATC')) else None,
                    "Dede(Baba)": fetch_person_by_tc(cursor_full, fetch_person_by_tc(cursor_full, main_person_dict.get('BABATC')).get('BABATC')) if main_person_dict.get('BABATC') and fetch_person_by_tc(cursor_full, main_person_dict.get('BABATC')) else None,
                }

                for rel_name, person in relations.items():
                    write_person_info_to_csv(writer, person, rel_name, cursor_address_local)

                relation_queries = {
                    "Çocuk": {
                        "criteria": "ANNETC = %s OR BABATC = %s",
                        "params_func": lambda p: (p['TC'], p['TC']),
                        "category_func": lambda p: CHILD_CATEGORIES[0] if p['CINSIYET'] == "Erkek" else CHILD_CATEGORIES[1]
                    },
                    "Kardeş": {
                        "criteria": "(ANNETC = %s OR BABATC = %s) AND TC != %s",
                        "params_func": lambda p: (p.get('ANNETC'), p.get('BABATC'), p['TC']),
                        "category_func": lambda p: SIBLING_CATEGORIES[0] if p['CINSIYET'] == "Erkek" else SIBLING_CATEGORIES[1] + (" Üvey" if p.get('ANNETC') != main_person_dict.get('ANNETC') or p.get('BABATC') != main_person_dict.get('BABATC') else "")
                    },
                    "Yeğen": {
                        "criteria": "ANNETC = %s OR BABATC = %s",
                        "params_func": lambda sibling: (sibling['TC'], sibling['TC']),
                        "category_func": lambda p: NIECE_NEPHEW_CATEGORIES[0]
                    },
                    "Amca/Hala": {
                        "criteria": "(ANNETC = %s OR BABATC = %s) AND TC NOT IN (%s, %s)",
                        "params_func": lambda parent_tc, main_tc: (fetch_person_by_tc(cursor_full, parent_tc).get('ANNETC'), fetch_person_by_tc(cursor_full, parent_tc).get('BABATC'), parent_tc, main_tc),
                        "category_func": lambda p, parent_key: UNCLE_AUNT_CATEGORIES[0] if p['CINSIYET'] == "Erkek" and parent_key == "Baba" else UNCLE_AUNT_CATEGORIES[1] if p['CINSIYET'] == "Kadın" and parent_key == "Baba" else UNCLE_AUNT_CATEGORIES[2] if p['CINSIYET'] == "Erkek" and parent_key == "Anne" else UNCLE_AUNT_CATEGORIES[3]
                    },
                    "Kuzen": {
                        "criteria": "ANNETC = %s OR BABATC = %s",
                        "params_func": lambda relative: (relative['TC'], relative['TC']),
                        "category_func": lambda p: COUSIN_CATEGORIES[0]
                    }
                }

                siblings = fetch_relatives_by_criteria(cursor_full, relation_queries["Kardeş"]["criteria"], relation_queries["Kardeş"]["params_func"](main_person_dict))
                for sibling in siblings:
                    write_person_info_to_csv(writer, sibling, relation_queries["Kardeş"]["category_func"](sibling), cursor_address_local)
                    nieces_nephews = fetch_relatives_by_criteria(cursor_full, relation_queries["Yeğen"]["criteria"], relation_queries["Yeğen"]["params_func"](sibling))
                    for niece_nephew in nieces_nephews:
                        write_person_info_to_csv(writer, niece_nephew, relation_queries["Yeğen"]["category_func"](niece_nephew), cursor_address_local)

                children = fetch_relatives_by_criteria(cursor_full, relation_queries["Çocuk"]["criteria"], relation_queries["Çocuk"]["params_func"](main_person_dict))
                for child in children:
                    write_person_info_to_csv(writer, child, relation_queries["Çocuk"]["category_func"](child), cursor_address_local)

                for parent_tc, parent_key in [(main_person_dict.get('BABATC'), "Baba"), (main_person_dict.get('ANNETC'), "Anne")]:
                    if parent_tc:
                        parent_person = fetch_person_by_tc(cursor_full, parent_tc)
                        if parent_person:
                            uncle_aunts = fetch_relatives_by_criteria(cursor_full, relation_queries["Amca/Hala"]["criteria"], relation_queries["Amca/Hala"]["params_func"](parent_tc, main_person_dict['TC']))
                            for relative in uncle_aunts:
                                category = relation_queries["Amca/Hala"]["category_func"](relative, parent_key)
                                write_person_info_to_csv(writer, relative, category, cursor_address_local)
                                cousins = fetch_relatives_by_criteria(cursor_full, relation_queries["Kuzen"]["criteria"], relation_queries["Kuzen"]["params_func"](relative))
                                for cousin in cousins:
                                    write_person_info_to_csv(writer, cousin, relation_queries["Kuzen"]["category_func"](cousin), cursor_address_local)

            return f"Kaydedildi: {filename}"

    except Exception as e:
        logging.error(f"An unexpected error occurred while processing TC {tc_no}: {e}", exc_info=True)
        return f"Beklenmeyen hata: {e}"

    finally:
        if cnx_full and cnx_full.is_connected():
            cnx_full.close()
            logging.debug(f"Fulldata database connection closed for TC {tc_no}")
        if cnx_address_local and cnx_address_local.is_connected():
            cnx_address_local.close()
            logging.debug(f"Address database connection closed for TC {tc_no}")

def main():
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("Sorgu")
    tk.Label(root, text="TC:").pack(pady=10)
    entry = tk.Entry(root)
    entry.pack(pady=10)

    def command():
        tc_number = entry.get()
        start_time = time.time()
        result = process_tc_number(tc_number)
        end_time = time.time()
        duration = end_time - start_time
        if result:
            messagebox.showinfo("Sonuç", f"{result} (Süre: {duration:.2f} saniye)")

    tk.Button(root, text="Sorgula", command=command).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    main()
