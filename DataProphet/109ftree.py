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

def write_person_info_to_csv(writer, person, category):
    writer.writerow([category] + list(person))

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

    # Anne ve babasının bilgilerini al
    anne_tc = main_person[7]  # ANNETC
    baba_tc = main_person[5]  # BABATC

    anne = get_person_by_tc(cursor, anne_tc) if anne_tc else None
    baba = get_person_by_tc(cursor, baba_tc) if baba_tc else None

    # Kardeşleri al
    siblings = get_siblings(cursor, anne_tc, baba_tc, tc_no)

    # Çocukları al
    children = get_children(cursor, tc_no)

    # CSV dosyası oluştur
    filename = f"./index/{main_person[1]}_{main_person[2]}.csv"
    with open(filename, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        # Başlıkları yaz
        writer.writerow(["Kategori", "TC", "AD", "SOYAD", "GSM", "BABAADI", "BABATC", "ANNEADI", "ANNETC", "DOGUMTARIHI", "OLUMTARIHI", "DOGUMYERI", "MEMLEKETIL", "MEMLEKETILCE", "MEMLEKETKOY", "ADRESIL", "ADRESILCE", "AILESIRANO", "BIREYSIRANO", "MEDENIHAL", "CINSIYET"])
        # Ana kaydı yaz
        write_person_info_to_csv(writer, main_person, "Ana Kayıt")
        # Anne bilgilerini yaz
        if anne:
            write_person_info_to_csv(writer, anne, "Anne")
        # Baba bilgilerini yaz
        if baba:
            write_person_info_to_csv(writer, baba, "Baba")
        # Kardeşleri yaz
        for sibling in siblings:
            category = ""
            # Üvey kardeş kontrolü
            is_step_sibling = sibling[7] != anne_tc or sibling[5] != baba_tc
            # Cinsiyete göre kategoriyi belirle
            if sibling[19] == "Erkek":
                category = "Erkek Kardeş"
            elif sibling[19] == "Kadın":
                category = "Kız Kardeş"
            # Eğer üvey kardeş ise, kategorinin sonuna "Üvey" ekleyin
            if is_step_sibling:
                category += " Üvey"
            write_person_info_to_csv(writer, sibling, category)

        # Çocukları yaz
        children_written = set()  # Yazılan çocukları takip etmek için bir küme
        for child in children:
            child_tc = child[0]
            if child_tc in children_written:
                continue  # Eğer çocuk zaten yazıldıysa, atla

            category = ""
            # Cinsiyete göre kategoriyi belirle
            if child[19] == "Erkek":
                category = "Oğlu"
            elif child[19] == "Kadın":
                category = "Kızı"
            write_person_info_to_csv(writer, child, category)
            children_written.add(child_tc)  # Yazılan çocuğu kümeye ekle

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
