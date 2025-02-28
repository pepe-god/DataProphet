#!/usr/bin/env python3
import mysql.connector
import csv
import configparser
import re

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['FULLDATA'], config['ADRESSDATA']

def validate_tc(tc_no):
    return len(tc_no) == 11 and tc_no.isdigit()

def connect_to_database(db_config):
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error:
        return None

def get_person_by_tc(cursor, tc_no):
    cursor.execute("SELECT TC, AD, SOYAD, GSM, BABAADI, BABATC, ANNEADI, ANNETC, DOGUMTARIHI, OLUMTARIHI, DOGUMYERI, MEMLEKETIL, MEMLEKETILCE, MEMLEKETKOY, ADRESIL, ADRESILCE, AILESIRANO, BIREYSIRANO, MEDENIHAL, CINSIYET FROM `109m` WHERE TC = %s", (tc_no,))
    return cursor.fetchone()

def get_relatives_by_criteria(cursor, criteria, params):
    query = "SELECT TC, AD, SOYAD, GSM, BABAADI, BABATC, ANNEADI, ANNETC, DOGUMTARIHI, OLUMTARIHI, DOGUMYERI, MEMLEKETIL, MEMLEKETILCE, MEMLEKETKOY, ADRESIL, ADRESILCE, AILESIRANO, BIREYSIRANO, MEDENIHAL, CINSIYET FROM `109m` WHERE " + criteria
    cursor.execute(query, params)
    return cursor.fetchall()

def get_address(db_address_config, tc_no):
    try:
        with mysql.connector.connect(**db_address_config) as cnx_address_local, cnx_address_local.cursor() as cursor_address_local:
            cursor_address_local.execute("SELECT GUNCELADRES FROM adresv2 WHERE TC = %s", (tc_no,))
            result = cursor_address_local.fetchone()
            return result[0] if result else None
    except mysql.connector.Error as e:
        print(f"Adres çekme hatası ({tc_no}): {e}")
        return None

def clean_address(address):
    return re.sub(r'\s+\S+\s+\S+\s+\S+$', '', address).strip() if address else ""

def write_person_info_to_csv(writer, person, category, db_address_config):
    if not person:
        return

    address = get_address(db_address_config, person[0])
    cleaned_address = clean_address(address)

    writer.writerow([category, *person[:4], person[8], person[9], person[10], person[11],
                     person[12], person[13], person[14], person[15], cleaned_address,
                     person[18], person[19], person[16], person[17]])

def process_tc_number(tc_no):
    if not validate_tc(tc_no):
        return "Geçersiz TC"

    db_full, db_address_config = read_config()
    cnx_full = connect_to_database(db_full)
    if not cnx_full:
        return "Veritabanı hatası"

    with cnx_full:
        cursor_full = cnx_full.cursor()
        main_person = get_person_by_tc(cursor_full, tc_no)

        if not main_person:
            return "Kayıt yok"

        filename = f"./index/{main_person[1]}_{main_person[2]}.csv"
        with open(filename, "w", encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Kategori", "TC", "AD", "SOYAD", "GSM", "DOGUMTARIHI", "OLUMTARIHI",
                             "DOGUMYERI", "MEMLEKETIL", "MEMLEKETILCE", "MEMLEKETKOY", "ADRESIL",
                             "ADRESILCE", "GUNCELADRES", "MEDENIHAL", "CINSIYET", "AILESIRANO", "BIREYSIRANO"])

            relations = {
                "Ana Kayıt": main_person,
                "Anne": get_person_by_tc(cursor_full, main_person[7]) if main_person[7] else None,
                "Baba": get_person_by_tc(cursor_full, main_person[5]) if main_person[5] else None,
                "Anneanne": get_person_by_tc(cursor_full, main_person[7] and get_person_by_tc(cursor_full, main_person[7])[7]) if main_person[7] else None,
                "Dede(Anne)": get_person_by_tc(cursor_full, main_person[7] and get_person_by_tc(cursor_full, main_person[7])[5]) if main_person[7] else None,
                "Babaanne": get_person_by_tc(cursor_full, main_person[5] and get_person_by_tc(cursor_full, main_person[5])[7]) if main_person[5] else None,
                "Dede(Baba)": get_person_by_tc(cursor_full, main_person[5] and get_person_by_tc(cursor_full, main_person[5])[5]) if main_person[5] else None,
            }

            for rel_name, person in relations.items():
                write_person_info_to_csv(writer, person, rel_name, db_address_config)

            relation_queries = {
                "Çocuk": {
                    "criteria": "ANNETC = %s OR BABATC = %s",
                    "params": lambda p: (p[0], p[0]),
                    "category": lambda p: "Oğlu" if p[19] == "Erkek" else "Kızı"
                },
                "Kardeş": {
                    "criteria": "(ANNETC = %s OR BABATC = %s) AND TC != %s",
                    "params": lambda p: (p[7], p[5], p[0]),
                    "category": lambda p: ("Erkek Kardeş" if p[19] == "Erkek" else "Kız Kardeş") + (" Üvey" if p[7] != main_person[7] or p[5] != main_person[5] else "")
                },
                "Yeğen": {
                    "criteria": "ANNETC = %s OR BABATC = %s",
                    "params": lambda sibling: (sibling[0], sibling[0]),
                    "category": lambda p: "Yeğen"
                },
                "Amca/Hala": {
                    "criteria": "(ANNETC = %s OR BABATC = %s) AND TC NOT IN (%s, %s)",
                    "params" : lambda parent_tc, main_tc: (get_person_by_tc(cursor_full, parent_tc)[7], get_person_by_tc(cursor_full, parent_tc)[5], parent_tc, main_tc),
                    "category": lambda p, parent_key: "Amca" if p[19] == "Erkek" and parent_key == "Baba" else "Hala" if p[19] == "Kadın" and parent_key == "Baba" else "Dayı" if p[19] == "Erkek" and parent_key == "Anne" else "Teyze"
                },
                "Kuzen": {
                    "criteria": "ANNETC = %s OR BABATC = %s",
                    "params": lambda relative: (relative[0], relative[0]),
                    "category": lambda p: "Kuzen"
                }
            }

            siblings = get_relatives_by_criteria(cursor_full, relation_queries["Kardeş"]["criteria"], relation_queries["Kardeş"]["params"](main_person))
            for sibling in siblings:
                write_person_info_to_csv(writer, sibling, relation_queries["Kardeş"]["category"](sibling), db_address_config)
                nieces_nephews = get_relatives_by_criteria(cursor_full, relation_queries["Yeğen"]["criteria"], relation_queries["Yeğen"]["params"](sibling))
                for niece_nephew in nieces_nephews:
                    write_person_info_to_csv(writer, niece_nephew, relation_queries["Yeğen"]["category"](niece_nephew), db_address_config)

            children = get_relatives_by_criteria(cursor_full, relation_queries["Çocuk"]["criteria"], relation_queries["Çocuk"]["params"](main_person))
            for child in children:
                write_person_info_to_csv(writer, child, relation_queries["Çocuk"]["category"](child), db_address_config)

            for parent_tc, parent_key in [(main_person[5], "Baba"), (main_person[7], "Anne")]:
                if parent_tc:
                    relatives = get_relatives_by_criteria(cursor_full, relation_queries["Amca/Hala"]["criteria"], relation_queries["Amca/Hala"]["params"](parent_tc, main_person[0]))
                    for relative in relatives:
                        category = relation_queries["Amca/Hala"]["category"](relative, parent_key)
                        write_person_info_to_csv(writer, relative, category, db_address_config)
                        cousins = get_relatives_by_criteria(cursor_full, relation_queries["Kuzen"]["criteria"], relation_queries["Kuzen"]["params"](relative))
                        for cousin in cousins:
                            write_person_info_to_csv(writer, cousin, relation_queries["Kuzen"]["category"](cousin), db_address_config)

        return f"Kaydedildi: {filename}"

def main():
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.title("Sorgu")
    tk.Label(root, text="TC:").pack(pady=10)
    entry = tk.Entry(root); entry.pack(pady=10)
    def command():
        result = process_tc_number(entry.get())
        if result:
            messagebox.showinfo("Sonuç", result)

    tk.Button(root, text="Sorgula", command=command).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    main()
