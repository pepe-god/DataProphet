#!/usr/bin/env python3
import configparser
import csv
import logging
import re
import time
import mysql.connector
import tkinter as tk
from tkinter import messagebox

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
        connection = mysql.connector.connect(**db_config, connection_timeout=10)
        logging.debug(f"Successfully connected to {db_name} database.")
        return connection
    except mysql.connector.Error as e:
        logging.error(f"Database connection error for {db_name}: {e}")
        return None

def fetch_person_by_tc(cursor, tc_no):
    if not tc_no:
        return None
    try:
        cursor.execute("SELECT " + ", ".join(DB_FIELDS) + " FROM `109m` WHERE TC = %s", (tc_no,))
        person_data = cursor.fetchone()
        if person_data:
            return dict(zip(DB_FIELDS, person_data))
        return None
    except mysql.connector.Error as e:
        logging.error(f"Error fetching person with TC {tc_no}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching person with TC {tc_no}: {e}", exc_info=True)
        return None


def fetch_relatives_by_criteria(cursor, criteria, params):
    if not params or (isinstance(params, tuple) and all(p is None for p in params)):
         return []
    try:
        query = "SELECT " + ", ".join(DB_FIELDS) + " FROM `109m` WHERE " + criteria
        cursor.execute(query, params)
        relative_data = cursor.fetchall()
        return [dict(zip(DB_FIELDS, person)) for person in relative_data]
    except mysql.connector.Error as e:
        logging.error(f"Error fetching relatives with criteria '{criteria}': {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching relatives with criteria '{criteria}': {e}", exc_info=True)
        return []


def fetch_address(cursor_address_local, tc_no):
    if not tc_no:
        return ""
    try:
        cursor_address_local.execute("SELECT GUNCELADRES FROM adresv2 WHERE TC = %s", (tc_no,))
        result = cursor_address_local.fetchone()
        return result[0] if result and result[0] else ""
    except mysql.connector.Error as e:
        logging.error(f"Address fetching error for TC {tc_no}: {e}")
        return ""
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching address for TC {tc_no}: {e}", exc_info=True)
        return ""

def clean_address(address):
    if not address:
        return ""
    return re.sub(r'\s+(\S+\s+){2}\S+$', '', address).strip()


def write_person_info_to_csv(writer, person_dict, category, cursor_address_local):
    if not person_dict:
        return

    address = fetch_address(cursor_address_local, person_dict.get('TC'))
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
    logging.info(f"Processing TC: {tc_no}")
    if not validate_tc(tc_no):
        logging.warning(f"Invalid TC format: {tc_no}")
        return "Geçersiz TC"

    db_full_config, db_address_config = read_config()

    cnx_full = None
    cnx_address_local = None
    cursor_full = None
    cursor_address_local = None

    try:
        cnx_full = connect_to_database(db_full_config, "fulldata")
        if not cnx_full:
            return "Veritabanı bağlantı hatası: Fulldata"

        cnx_address_local = connect_to_database(db_address_config, "address")
        if not cnx_address_local:
            if cnx_full and cnx_full.is_connected():
                cnx_full.close()
            return "Veritabanı bağlantı hatası: Adres"

        cursor_full = cnx_full.cursor(buffered=True)
        cursor_address_local = cnx_address_local.cursor(buffered=True)
        logging.debug("Cursors created.")

        main_person_dict = fetch_person_by_tc(cursor_full, tc_no)
        if not main_person_dict:
            logging.info(f"No record found for TC: {tc_no}")
            return "Kayıt yok"

        filename = f"./index/{main_person_dict.get('AD', 'Bilinmeyen')}_{main_person_dict.get('SOYAD', 'Bilinmeyen')}.csv"
        logging.info(f"Writing family information for TC: {tc_no} to file: {filename}")

        with open(filename, "w", encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER)

            relations = {
                "Ana Kayıt": main_person_dict,
                "Anne": fetch_person_by_tc(cursor_full, main_person_dict.get('ANNETC')),
                "Baba": fetch_person_by_tc(cursor_full, main_person_dict.get('BABATC')),
            }

            anne_person = relations.get("Anne")
            baba_person = relations.get("Baba")

            relations["Anneanne"] = fetch_person_by_tc(cursor_full, anne_person.get('ANNETC')) if anne_person else None
            relations["Dede(Anne)"] = fetch_person_by_tc(cursor_full, anne_person.get('BABATC')) if anne_person else None
            relations["Babaanne"] = fetch_person_by_tc(cursor_full, baba_person.get('ANNETC')) if baba_person else None
            relations["Dede(Baba)"] = fetch_person_by_tc(cursor_full, baba_person.get('BABATC')) if baba_person else None


            for rel_name, person in relations.items():
                write_person_info_to_csv(writer, person, rel_name, cursor_address_local)

            relation_queries = {
                "Çocuk": {
                    "criteria": "ANNETC = %s OR BABATC = %s",
                    "params_func": lambda p_tc: (p_tc, p_tc),
                    "category_func": lambda p: CHILD_CATEGORIES[0] if p.get('CINSIYET') == "Erkek" else CHILD_CATEGORIES[1] if p.get('CINSIYET') == "Kadın" else "Çocuk"
                },
                "Kardeş": {
                    "criteria": "(ANNETC = %s OR BABATC = %s) AND TC != %s",
                    "params_func": lambda anne_tc, baba_tc, main_tc: (anne_tc, baba_tc, main_tc),
                    "category_func": lambda p, main_person: SIBLING_CATEGORIES[0] if p.get('CINSIYET') == "Erkek" else SIBLING_CATEGORIES[1] + (" (Üvey)" if (p.get('ANNETC') != main_person.get('ANNETC') or p.get('BABATC') != main_person.get('BABATC')) else "")
                },
                 "Yeğen": {
                    "criteria": "ANNETC = %s OR BABATC = %s",
                    "params_func": lambda sibling_tc: (sibling_tc, sibling_tc),
                    "category_func": lambda p: NIECE_NEPHEW_CATEGORIES[0]
                },
                "Amca/Hala/Dayı/Teyze": {
                    "criteria": "(ANNETC = %s OR BABATC = %s) AND TC != %s",
                    "params_func": lambda ebeveyn_anne_tc, ebeveyn_baba_tc, ebeveyn_tc: (ebeveyn_anne_tc, ebeveyn_baba_tc, ebeveyn_tc),
                    "category_func": lambda p, ebeveyn_key: UNCLE_AUNT_CATEGORIES[0] if p.get('CINSIYET') == "Erkek" and ebeveyn_key == "Baba" else UNCLE_AUNT_CATEGORIES[1] if p.get('CINSIYET') == "Kadın" and ebeveyn_key == "Baba" else UNCLE_AUNT_CATEGORIES[2] if p.get('CINSIYET') == "Erkek" and ebeveyn_key == "Anne" else UNCLE_AUNT_CATEGORIES[3] if p.get('CINSIYET') == "Kadın" and ebeveyn_key == "Anne" else "Bilinmeyen Amca/Hala/Dayı/Teyze"
                },
                "Kuzen": {
                     "criteria": "ANNETC = %s OR BABATC = %s",
                     "params_func": lambda relative_tc: (relative_tc, relative_tc),
                     "category_func": lambda p: COUSIN_CATEGORIES[0]
                }
            }

            siblings = fetch_relatives_by_criteria(
                cursor_full,
                relation_queries["Kardeş"]["criteria"],
                relation_queries["Kardeş"]["params_func"](
                    main_person_dict.get('ANNETC'),
                    main_person_dict.get('BABATC'),
                    main_person_dict.get('TC')
                )
            )
            for sibling in siblings:
                write_person_info_to_csv(writer, sibling, relation_queries["Kardeş"]["category_func"](sibling, main_person_dict), cursor_address_local)
                nieces_nephews = fetch_relatives_by_criteria(
                    cursor_full,
                    relation_queries["Yeğen"]["criteria"],
                    relation_queries["Yeğen"]["params_func"](sibling.get('TC'))
                )
                for niece_nephew in nieces_nephews:
                     write_person_info_to_csv(writer, niece_nephew, relation_queries["Yeğen"]["category_func"](niece_nephew), cursor_address_local)


            children = fetch_relatives_by_criteria(
                cursor_full,
                relation_queries["Çocuk"]["criteria"],
                relation_queries["Çocuk"]["params_func"](main_person_dict.get('TC'))
            )
            for child in children:
                write_person_info_to_csv(writer, child, relation_queries["Çocuk"]["category_func"](child), cursor_address_local)

            for parent_tc, parent_key in [(main_person_dict.get('BABATC'), "Baba"), (main_person_dict.get('ANNETC'), "Anne")]:
                 if parent_tc:
                    parent_person = fetch_person_by_tc(cursor_full, parent_tc)
                    if parent_person:
                        uncle_aunts_dayi_teyzes = fetch_relatives_by_criteria(
                            cursor_full,
                            relation_queries["Amca/Hala/Dayı/Teyze"]["criteria"],
                            relation_queries["Amca/Hala/Dayı/Teyze"]["params_func"](
                                parent_person.get('ANNETC'),
                                parent_person.get('BABATC'),
                                parent_tc
                                )
                        )
                        for relative in uncle_aunts_dayi_teyzes:
                             category = relation_queries["Amca/Hala/Dayı/Teyze"]["category_func"](relative, parent_key)
                             write_person_info_to_csv(writer, relative, category, cursor_address_local)

                             cousins = fetch_relatives_by_criteria(
                                cursor_full,
                                relation_queries["Kuzen"]["criteria"],
                                relation_queries["Kuzen"]["params_func"](relative.get('TC'))
                            )
                             for cousin in cousins:
                                 write_person_info_to_csv(writer, cousin, relation_queries["Kuzen"]["category_func"](cousin), cursor_address_local)


        logging.info(f"Family information for TC: {tc_no} written to file: {filename}")
        return f"Kaydedildi: {filename}"

    except Exception as e:
        logging.error(f"An unexpected error occurred while processing TC {tc_no}: {e}", exc_info=True)
        return f"Beklenmeyen hata: {e}"

    finally:
        if cursor_full:
            cursor_full.close()
            logging.debug(f"Fulldata cursor closed for TC {tc_no}")
        if cursor_address_local:
            cursor_address_local.close()
            logging.debug(f"Address cursor closed for TC {tc_no}")
        if cnx_full and cnx_full.is_connected():
            cnx_full.close()
            logging.debug(f"Fulldata database connection closed for TC {tc_no}")
        if cnx_address_local and cnx_address_local.is_connected():
            cnx_address_local.close()
            logging.debug(f"Address database connection closed for TC {tc_no}")
        logging.info(f"Finished processing TC: {tc_no}")


def main():
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
        messagebox.showinfo("Sonuç", f"{result} (Süre: {duration:.2f} saniye)")

    tk.Button(root, text="Sorgula", command=command).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    main()
