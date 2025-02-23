#!/usr/bin/env python3
import mysql.connector
import csv
import configparser
import tkinter as tk
from tkinter import messagebox
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

def get_siblings(cursor, anne_tc, baba_tc, tc_no):
    cursor.execute("SELECT TC, AD, SOYAD, GSM, BABAADI, BABATC, ANNEADI, ANNETC, DOGUMTARIHI, OLUMTARIHI, DOGUMYERI, MEMLEKETIL, MEMLEKETILCE, MEMLEKETKOY, ADRESIL, ADRESILCE, AILESIRANO, BIREYSIRANO, MEDENIHAL, CINSIYET FROM `109m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s", (anne_tc, baba_tc, tc_no))
    return cursor.fetchall()

def get_children(cursor, parent_tc):
    cursor.execute("SELECT TC, AD, SOYAD, GSM, BABAADI, BABATC, ANNEADI, ANNETC, DOGUMTARIHI, OLUMTARIHI, DOGUMYERI, MEMLEKETIL, MEMLEKETILCE, MEMLEKETKOY, ADRESIL, ADRESILCE, AILESIRANO, BIREYSIRANO, MEDENIHAL, CINSIYET FROM `109m` WHERE ANNETC = %s OR BABATC = %s", (parent_tc, parent_tc))
    return cursor.fetchall()

def get_relatives(cursor, anne_tc, baba_tc, exclude_tc):
    cursor.execute("SELECT TC, AD, SOYAD, GSM, BABAADI, BABATC, ANNEADI, ANNETC, DOGUMTARIHI, OLUMTARIHI, DOGUMYERI, MEMLEKETIL, MEMLEKETILCE, MEMLEKETKOY, ADRESIL, ADRESILCE, AILESIRANO, BIREYSIRANO, MEDENIHAL, CINSIYET FROM `109m` WHERE (ANNETC = %s OR BABATC = %s) AND TC NOT IN (%s, %s)", (anne_tc, baba_tc, exclude_tc, exclude_tc))
    return cursor.fetchall()


def write_person_info_to_csv(writer, person, category):
    if not person:
        return

    db_address_config = read_config()[1]

    try:
        with mysql.connector.connect(**db_address_config) as cnx_address_local, cnx_address_local.cursor() as cursor_address_local:
            cursor_address_local.execute("SELECT GUNCELADRES FROM adresv2 WHERE TC = %s", (person[0],))
            result = cursor_address_local.fetchone()
            address = result[0] if result else None
    except mysql.connector.Error as e:
        print(f"Adres çekme hatası ({person[0]}): {e}")  # Hata mesajını yazdır
        address = None  # Adresi None olarak ayarla, hatayı yoksay

    address = re.sub(r'\s+\S+\s+\S+\s+\S+$', '', address).strip() if address else ""
    writer.writerow([category, *person[:4], person[8], person[9], person[10], person[11],
                     person[12], person[13], person[14], person[15], address,
                     person[18], person[19], person[16], person[17]])


def process_tc_number(tc_no):
    if not validate_tc(tc_no):
        messagebox.showerror("Hata", "Geçersiz TC")
        return

    db_full, _ = read_config()
    cnx_full = connect_to_database(db_full)
    if not cnx_full:
        messagebox.showerror("Hata", "Veritabanı hatası")
        return

    cursor_full = cnx_full.cursor()

    main_person = get_person_by_tc(cursor_full, tc_no)

    if not main_person:
        messagebox.showinfo("Bulunamadı", "Kayıt yok")
        cnx_full.close()
        return

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
            write_person_info_to_csv(writer, person, rel_name)

        queries = {
            "Çocuk": (get_children, (tc_no,), lambda p: "Oğlu" if p[19] == "Erkek" else "Kızı"),
            "Kardeş": (get_siblings, (main_person[7], main_person[5], tc_no),
                      lambda p: ("Erkek Kardeş" if p[19] == "Erkek" else "Kız Kardeş") + (" Üvey" if p[7] != main_person[7] or p[5] != main_person[5] else "")),
            "Yeğen": (get_children, lambda sibling: (sibling[0],), lambda p: "Yeğen"),
            "Amca/Hala": (get_relatives, lambda parent: (get_person_by_tc(cursor_full, parent)[7], get_person_by_tc(cursor_full, parent)[5], parent),
                          lambda p, parent_key: "Amca" if p[19] == "Erkek" and parent_key == "Baba" else "Hala" if p[19] == "Kadın" and parent_key == "Baba" else "Dayı" if p[19] == "Erkek" and parent_key == "Anne" else "Teyze"),
            "Kuzen": (get_children, lambda relative: (relative[0],), lambda p: "Kuzen"),
        }

        for child in queries["Çocuk"][0](cursor_full, *queries["Çocuk"][1]):
            write_person_info_to_csv(writer, child, queries["Çocuk"][2](child))

        for sibling in queries["Kardeş"][0](cursor_full, *queries["Kardeş"][1]):
            write_person_info_to_csv(writer, sibling, queries["Kardeş"][2](sibling))
            for niece_nephew in queries["Yeğen"][0](cursor_full, *queries["Yeğen"][1](sibling)):
                write_person_info_to_csv(writer, niece_nephew, queries["Yeğen"][2](niece_nephew))

        for parent_tc, parent_key in [(main_person[5], "Baba"), (main_person[7], "Anne")]:
            if parent_tc:
                for relative in queries["Amca/Hala"][0](cursor_full, *queries["Amca/Hala"][1](parent_tc)):
                    category = queries["Amca/Hala"][2](relative, parent_key)
                    write_person_info_to_csv(writer, relative, category)
                    for cousin in queries["Kuzen"][0](cursor_full, *queries["Kuzen"][1](relative)):
                        write_person_info_to_csv(writer, cousin, queries["Kuzen"][2](cousin))

    messagebox.showinfo("Başarılı", f"Kaydedildi: {filename}")  # Her zaman "Kaydedildi" mesajını göster
    cnx_full.close()


def main():
    root = tk.Tk()
    root.title("Sorgu")
    tk.Label(root, text="TC:").pack(pady=10)
    entry = tk.Entry(root); entry.pack(pady=10)
    tk.Button(root, text="Sorgula", command=lambda: process_tc_number(entry.get())).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    main()
