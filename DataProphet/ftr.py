#!/usr/bin/env python3
import mysql.connector
import csv
import logging
import configparser
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['FULLDATA'], config['ADRESSDATA']

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

def get_current_address(cursor, tc_no):
    query = "SELECT GUNCELADRES FROM adresv2 WHERE TC = %s"
    cursor.execute(query, (tc_no,))
    result = cursor.fetchone()
    cursor.fetchall()
    return result[0] if result else None

def write_person_info_to_csv(writer, person, category, current_address):
    # GUNCELADRES alanının son 3 kısmını (boşluklar dahil) kaldır
    if current_address:
        # Regex ile son 3 kelimeyi bul ve kaldır
        pattern = re.compile(r'\s+\S+\s+\S+\s+\S+$')  # Son 3 kelime ve aralarındaki boşluklar
        current_address = pattern.sub("", current_address).strip()

    # CSV'ye yaz
    writer.writerow([
        category, person[0], person[1], person[2], person[3], person[8], person[9], person[10],
        person[11], person[12], person[13], person[14], person[15], current_address,
        person[18], person[19], person[16], person[17]
    ])

def process_tc_number(tc_no):
    if not validate_tc(tc_no):
        messagebox.showerror("Hata", "Geçersiz TC Kimlik Numarası!")
        return

    db_config_fulldata, db_config_adressdata = read_config()
    cnx_fulldata = connect_to_database(db_config_fulldata)
    cnx_adressdata = connect_to_database(db_config_adressdata)
    if not cnx_fulldata or not cnx_adressdata:
        messagebox.showerror("Hata", "Veritabanına bağlanılamadı.")
        return

    cursor_fulldata = cnx_fulldata.cursor()
    cursor_adressdata = cnx_adressdata.cursor()
    main_person = get_person_by_tc(cursor_fulldata, tc_no)

    if not main_person:
        messagebox.showinfo("Bulunamadı", "Girilen TC Kimlik Numarası ile eşleşen kayıt bulunamadı.")
        cursor_fulldata.close()
        cursor_adressdata.close()
        cnx_fulldata.close()
        cnx_adressdata.close()
        return

    anne_tc = main_person[7]
    baba_tc = main_person[5]

    anne = get_person_by_tc(cursor_fulldata, anne_tc) if anne_tc else None
    baba = get_person_by_tc(cursor_fulldata, baba_tc) if baba_tc else None

    if anne:
        anne_anne_tc = anne[7]
        anne_baba_tc = anne[5]
        anne_anne = get_person_by_tc(cursor_fulldata, anne_anne_tc) if anne_anne_tc else None
        anne_baba = get_person_by_tc(cursor_fulldata, anne_baba_tc) if anne_baba_tc else None
    else:
        anne_anne = None
        anne_baba = None

    if baba:
        baba_anne_tc = baba[7]
        baba_baba_tc = baba[5]
        baba_anne = get_person_by_tc(cursor_fulldata, baba_anne_tc) if baba_anne_tc else None
        baba_baba = get_person_by_tc(cursor_fulldata, baba_baba_tc) if baba_baba_tc else None
    else:
        baba_anne = None
        baba_baba = None

    siblings = get_siblings(cursor_fulldata, anne_tc, baba_tc, tc_no)
    children = get_children(cursor_fulldata, tc_no)
    baba_relatives = get_relatives(cursor_fulldata, baba_anne_tc, baba_baba_tc, baba_tc) if baba else []
    anne_relatives = get_relatives(cursor_fulldata, anne_anne_tc, anne_baba_tc, anne_tc) if anne else []

    filename = f"./index/{main_person[1]}_{main_person[2]}.csv"
    with open(filename, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Kategori", "TC", "AD", "SOYAD", "GSM", "DOGUMTARIHI", "OLUMTARIHI", "DOGUMYERI", "MEMLEKETIL", "MEMLEKETILCE", "MEMLEKETKOY", "ADRESIL", "ADRESILCE", "GUNCELADRES", "MEDENIHAL", "CINSIYET", "AILESIRANO", "BIREYSIRANO"])

        # Ana Kayıt
        current_address = get_current_address(cursor_adressdata, main_person[0])
        write_person_info_to_csv(writer, main_person, "Ana Kayıt", current_address)

        # Anne
        if anne:
            current_address = get_current_address(cursor_adressdata, anne[0])
            write_person_info_to_csv(writer, anne, "Anne", current_address)

        # Baba
        if baba:
            current_address = get_current_address(cursor_adressdata, baba[0])
            write_person_info_to_csv(writer, baba, "Baba", current_address)

        # Anneanne
        if anne_anne:
            current_address = get_current_address(cursor_adressdata, anne_anne[0])
            write_person_info_to_csv(writer, anne_anne, "Anneanne", current_address)

        # Dede
        if anne_baba:
            current_address = get_current_address(cursor_adressdata, anne_baba[0])
            write_person_info_to_csv(writer, anne_baba, "Dede", current_address)

        # Babaanne
        if baba_anne:
            current_address = get_current_address(cursor_adressdata, baba_anne[0])
            write_person_info_to_csv(writer, baba_anne, "Babaanne", current_address)

        # Dede
        if baba_baba:
            current_address = get_current_address(cursor_adressdata, baba_baba[0])
            write_person_info_to_csv(writer, baba_baba, "Dede", current_address)

        # Çocuklar
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
            current_address = get_current_address(cursor_adressdata, child_tc)
            write_person_info_to_csv(writer, child, category, current_address)
            children_written.add(child_tc)

        # Kardeşler
        for sibling in siblings:
            category = ""
            is_step_sibling = sibling[7] != anne_tc or sibling[5] != baba_tc
            if sibling[19] == "Erkek":
                category = "Erkek Kardeş"
            elif sibling[19] == "Kadın":
                category = "Kız Kardeş"
            if is_step_sibling:
                category += " Üvey"
            current_address = get_current_address(cursor_adressdata, sibling[0])
            write_person_info_to_csv(writer, sibling, category, current_address)
            nieces_and_nephews = get_children(cursor_fulldata, sibling[0])
            for niece_or_nephew in nieces_and_nephews:
                current_address = get_current_address(cursor_adressdata, niece_or_nephew[0])
                write_person_info_to_csv(writer, niece_or_nephew, "Yeğen", current_address)

        # Baba Tarafı
        for relative in baba_relatives:
            category = "Baba Tarafı"
            if relative[19] == "Erkek":
                category = "Amca"
            elif relative[19] == "Kadın":
                category = "Hala"
            current_address = get_current_address(cursor_adressdata, relative[0])
            write_person_info_to_csv(writer, relative, category, current_address)
            cousins = get_children(cursor_fulldata, relative[0])
            for cousin in cousins:
                current_address = get_current_address(cursor_adressdata, cousin[0])
                write_person_info_to_csv(writer, cousin, "Kuzen", current_address)

        # Anne Tarafı
        for relative in anne_relatives:
            category = "Anne Tarafı"
            if relative[19] == "Erkek":
                category = "Dayı"
            elif relative[19] == "Kadın":
                category = "Teyze"
            current_address = get_current_address(cursor_adressdata, relative[0])
            write_person_info_to_csv(writer, relative, category, current_address)
            cousins = get_children(cursor_fulldata, relative[0])
            for cousin in cousins:
                current_address = get_current_address(cursor_adressdata, cousin[0])
                write_person_info_to_csv(writer, cousin, "Kuzen", current_address)

    messagebox.showinfo("Başarılı", f"Kişi ve ailesi bilgileri {filename} dosyasına kaydedildi.")

    cursor_fulldata.close()
    cursor_adressdata.close()
    cnx_fulldata.close()
    cnx_adressdata.close()

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
