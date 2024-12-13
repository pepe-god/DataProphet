#!/usr/bin/env python3
import mysql.connector
import csv
import logging
import configparser
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['FULLDATA']

def validate_tc(tc_no):
    return len(tc_no) == 11 and tc_no.isdigit()

def connect_to_database(db_config):
    try:
        cnx = mysql.connector.connect(**db_config)
        logger.info("Veritabanına başarıyla bağlandı.")
        return cnx
    except Error as e:
        logger.error(f"Veritabanına bağlanırken hata oluştu: {e}")
        return None

def get_person_by_tc(cursor, tc_no):
    query = "SELECT TC, AD, SOYAD, GSM, BABAADI, BABATC, ANNEADI, ANNETC, DOGUMTARIHI, OLUMTARIHI, DOGUMYERI, MEMLEKETIL, MEMLEKETILCE, MEMLEKETKOY, ADRESIL, ADRESILCE, AILESIRANO, BIREYSIRANO, MEDENIHAL, CINSIYET FROM `109m` WHERE TC = %s"
    cursor.execute(query, (tc_no,))
    result = cursor.fetchone()
    return result

def get_siblings(cursor, anne_tc, baba_tc, tc_no):
    query = "SELECT TC, AD, SOYAD, GSM, BABAADI, BABATC, ANNEADI, ANNETC, DOGUMTARIHI, OLUMTARIHI, DOGUMYERI, MEMLEKETIL, MEMLEKETILCE, MEMLEKETKOY, ADRESIL, ADRESILCE, AILESIRANO, BIREYSIRANO, MEDENIHAL, CINSIYET FROM `109m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s"
    cursor.execute(query, (anne_tc, baba_tc, tc_no))
    return cursor.fetchall()

def get_children(cursor, parent_tc):
    query = "SELECT TC, AD, SOYAD, GSM, BABAADI, BABATC, ANNEADI, ANNETC, DOGUMTARIHI, OLUMTARIHI, DOGUMYERI, MEMLEKETIL, MEMLEKETILCE, MEMLEKETKOY, ADRESIL, ADRESILCE, AILESIRANO, BIREYSIRANO, MEDENIHAL, CINSIYET FROM `109m` WHERE ANNETC = %s OR BABATC = %s"
    cursor.execute(query, (parent_tc, parent_tc))
    return cursor.fetchall()

def get_relatives(cursor, anne_tc, baba_tc, exclude_tc):
    query = """
    SELECT TC, AD, SOYAD, GSM, BABAADI, BABATC, ANNEADI, ANNETC, DOGUMTARIHI, OLUMTARIHI, DOGUMYERI, MEMLEKETIL, MEMLEKETILCE, MEMLEKETKOY, ADRESIL, ADRESILCE, AILESIRANO, BIREYSIRANO, MEDENIHAL, CINSIYET
    FROM `109m`
    WHERE (ANNETC = %s OR BABATC = %s)
    AND TC NOT IN (%s, %s)
    """
    cursor.execute(query, (anne_tc, baba_tc, exclude_tc, exclude_tc))
    return cursor.fetchall()

def write_person_info_to_csv(writer, person, category):
    writer.writerow([category] + list(person[:4]) + list(person[8:16]) + list(person[17:]) + [person[16], person[17]])

def process_tc_number(tc_no):
    if not validate_tc(tc_no):
        messagebox.showerror("Hata", "Geçersiz TC Kimlik Numarası!")
        return

    db_config = read_config()
    cnx = connect_to_database(db_config)
    if not cnx:
        messagebox.showerror("Hata", "Veritabanına bağlanılamadı.")
        return

    cursor = cnx.cursor()
    main_person = get_person_by_tc(cursor, tc_no)

    if not main_person:
        messagebox.showinfo("Bulunamadı", "Girilen TC Kimlik Numarası ile eşleşen kayıt bulunamadı.")
        cursor.close()
        cnx.close()
        return

    anne_tc = main_person[7]
    baba_tc = main_person[5]

    anne = get_person_by_tc(cursor, anne_tc) if anne_tc else None
    baba = get_person_by_tc(cursor, baba_tc) if baba_tc else None

    if anne:
        anne_anne_tc = anne[7]
        anne_baba_tc = anne[5]
        anne_anne = get_person_by_tc(cursor, anne_anne_tc) if anne_anne_tc else None
        anne_baba = get_person_by_tc(cursor, anne_baba_tc) if anne_baba_tc else None
    else:
        anne_anne = None
        anne_baba = None

    if baba:
        baba_anne_tc = baba[7]
        baba_baba_tc = baba[5]
        baba_anne = get_person_by_tc(cursor, baba_anne_tc) if baba_anne_tc else None
        baba_baba = get_person_by_tc(cursor, baba_baba_tc) if baba_baba_tc else None
    else:
        baba_anne = None
        baba_baba = None

    siblings = get_siblings(cursor, anne_tc, baba_tc, tc_no)
    children = get_children(cursor, tc_no)
    baba_relatives = get_relatives(cursor, baba_anne_tc, baba_baba_tc, baba_tc) if baba else []
    anne_relatives = get_relatives(cursor, anne_anne_tc, anne_baba_tc, anne_tc) if anne else []

    filename = f"./index/{main_person[1]}_{main_person[2]}.csv"
    with open(filename, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Kategori", "TC", "AD", "SOYAD", "GSM", "DOGUMTARIHI", "OLUMTARIHI", "DOGUMYERI", "MEMLEKETIL", "MEMLEKETILCE", "MEMLEKETKOY", "ADRESIL", "ADRESILCE", "AILESIRANO", "BIREYSIRANO", "MEDENIHAL", "CINSIYET"])
        write_person_info_to_csv(writer, main_person, "Ana Kayıt")
        if anne:
            write_person_info_to_csv(writer, anne, "Anne")
        if baba:
            write_person_info_to_csv(writer, baba, "Baba")
        if anne_anne:
            write_person_info_to_csv(writer, anne_anne, "Anneanne")
        if anne_baba:
            write_person_info_to_csv(writer, anne_baba, "Dede")
        if baba_anne:
            write_person_info_to_csv(writer, baba_anne, "Babaanne")
        if baba_baba:
            write_person_info_to_csv(writer, baba_baba, "Dede")
        children_written = set()
        for child in children:
            child_tc = child[0]
            if child_tc in children_written:
                continue
            category = ""
            if child[19] == "Erkek":
                category = "Oğlu"
            elif child[19] == "Kadın":
                category = "Kızı"
            write_person_info_to_csv(writer, child, category)
            children_written.add(child_tc)
        for sibling in siblings:
            category = ""
            is_step_sibling = sibling[7] != anne_tc or sibling[5] != baba_tc
            if sibling[19] == "Erkek":
                category = "Erkek Kardeş"
            elif sibling[19] == "Kadın":
                category = "Kız Kardeş"
            if is_step_sibling:
                category += " Üvey"
            write_person_info_to_csv(writer, sibling, category)
            nieces_and_nephews = get_children(cursor, sibling[0])
            for niece_or_nephew in nieces_and_nephews:
                write_person_info_to_csv(writer, niece_or_nephew, "Yeğen")
        for relative in baba_relatives:
            category = "Baba Tarafı"
            if relative[19] == "Erkek":
                category = "Amca"
            elif relative[19] == "Kadın":
                category = "Hala"
            write_person_info_to_csv(writer, relative, category)
            cousins = get_children(cursor, relative[0])
            for cousin in cousins:
                write_person_info_to_csv(writer, cousin, "Kuzen")
        for relative in anne_relatives:
            category = "Anne Tarafı"
            if relative[19] == "Erkek":
                category = "Dayı"
            elif relative[19] == "Kadın":
                category = "Teyze"
            write_person_info_to_csv(writer, relative, category)
            cousins = get_children(cursor, relative[0])
            for cousin in cousins:
                write_person_info_to_csv(writer, cousin, "Kuzen")

    messagebox.showinfo("Başarılı", f"Kişi ve ailesi bilgileri {filename} dosyasına kaydedildi.")

    cursor.close()
    cnx.close()

def main():
    root = tk.Tk()
    root.title("Kişi ve Ailesi Bilgisi Sorgulama")

    tk.Label(root, text="TC Kimlik Numarası:").pack(pady=10)
    entry = tk.Entry(root, width=30)
    entry.pack(pady=10)
    tk.Button(root, text="Sorgula", command=lambda: process_tc_number(entry.get())).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
