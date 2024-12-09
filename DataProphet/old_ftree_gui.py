#!/usr/bin/env python3
import mysql.connector
import csv
import os
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
    return config['DATABASE'], config['GSMDATA']

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

def execute_query(cursor, query, params=None):
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Error as e:
        logger.error(f"Sorgu çalıştırılırken hata oluştu: {e}")
        return None

def get_family_member_by_tc(cursor, tc_no):
    query = "SELECT * FROM `101m` WHERE TC = %s"
    result = execute_query(cursor, query, (tc_no,))
    return result[0] if result else None

def get_children_by_parent_tc(cursor, parent_tc):
    query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
    return execute_query(cursor, query, (parent_tc, parent_tc))

def get_siblings_by_parent_tc(cursor, anne_tc, baba_tc, tc_no):
    query = "SELECT * FROM `101m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s"
    return execute_query(cursor, query, (anne_tc, baba_tc, tc_no))

def get_cousins_by_parent_tc_list(cursor, parent_tc_list):
    if parent_tc_list:
        query = "SELECT * FROM `101m` WHERE ANNETC IN (%s) OR BABATC IN (%s)" % (','.join(['%s'] * len(parent_tc_list)), ','.join(['%s'] * len(parent_tc_list)))
        return execute_query(cursor, query, parent_tc_list + parent_tc_list)
    return []

def get_gsm_data_by_tc(cursor, tc_no):
    query = "SELECT GSM FROM `gsmdata` WHERE TC = %s"
    result = execute_query(cursor, query, (tc_no,))
    return ", ".join([gsm[0] for gsm in result]) if result else "Yok"

def write_person_info(writer, person, category, gsm_data=None):
    writer.writerow([category] + [str(value) for value in person[1:]] + ([gsm_data] if gsm_data else []))

def process_family_tree(cursor, gsm_cursor, tc_no, writer, prefix=""):
    main_person = get_family_member_by_tc(cursor, tc_no)
    if not main_person:
        return

    gsm_data = get_gsm_data_by_tc(gsm_cursor, tc_no)
    write_person_info(writer, main_person, prefix + "Ana Kayıt", gsm_data)

    anne_tc, baba_tc = main_person[8], main_person[10]
    parents = [(anne_tc, "Anne"), (baba_tc, "Baba")]
    for parent_tc, parent_name in parents:
        parent_result = get_family_member_by_tc(cursor, parent_tc)
        if parent_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, parent_tc)
            write_person_info(writer, parent_result, prefix + parent_name, gsm_data)

            grandparent_tcs = [parent_result[8], parent_result[10]]
            for grandparent_tc in grandparent_tcs:
                grandparent_result = get_family_member_by_tc(cursor, grandparent_tc)
                if grandparent_result:
                    gsm_data = get_gsm_data_by_tc(gsm_cursor, grandparent_tc)
                    write_person_info(writer, grandparent_result, prefix + f"{parent_name}'nin {('Anne', 'Baba')[grandparent_tc == parent_result[10]]}", gsm_data)

    children_result = get_children_by_parent_tc(cursor, tc_no)
    for child in children_result:
        gsm_data = get_gsm_data_by_tc(gsm_cursor, child[1])
        write_person_info(writer, child, prefix + "Çocuk", gsm_data)

        grandchildren_result = get_children_by_parent_tc(cursor, child[1])
        for grandchild in grandchildren_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, grandchild[1])
            write_person_info(writer, grandchild, prefix + f"{child[2]} {child[3]}'in Çocuğu", gsm_data)

    siblings_result = get_siblings_by_parent_tc(cursor, anne_tc, baba_tc, tc_no)
    for sibling in siblings_result:
        gsm_data = get_gsm_data_by_tc(gsm_cursor, sibling[1])
        write_person_info(writer, sibling, prefix + "Kardeşi", gsm_data)

        nephews_result = get_children_by_parent_tc(cursor, sibling[1])
        for nephew in nephews_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, nephew[1])
            write_person_info(writer, nephew, prefix + "Yeğeni", gsm_data)

            grandnephews_result = get_children_by_parent_tc(cursor, nephew[1])
            for grandnephew in grandnephews_result:
                gsm_data = get_gsm_data_by_tc(gsm_cursor, grandnephew[1])
                write_person_info(writer, grandnephew, prefix + f"{nephew[2]} {nephew[3]}'in Çocuğu", gsm_data)

    aunts_uncles_tc_list = []
    for parent_tc in [anne_tc, baba_tc]:
        if parent_tc:
            parent_result = get_family_member_by_tc(cursor, parent_tc)
            if parent_result:
                aunts_uncles_result = get_siblings_by_parent_tc(cursor, parent_result[8], parent_result[10], parent_result[1])
                if aunts_uncles_result:
                    aunts_uncles_tc_list.extend([aunt_uncle[1] for aunt_uncle in aunts_uncles_result])
                    for aunt_uncle in aunts_uncles_result:
                        gsm_data = get_gsm_data_by_tc(gsm_cursor, aunt_uncle[1])
                        write_person_info(writer, aunt_uncle, prefix + "Dayı/Teyze" if parent_tc == anne_tc else "Amca/Hala", gsm_data)

    cousins_result = get_cousins_by_parent_tc_list(cursor, aunts_uncles_tc_list)
    for cousin in cousins_result:
        gsm_data = get_gsm_data_by_tc(gsm_cursor, cousin[1])
        write_person_info(writer, cousin, prefix + "Kuzen", gsm_data)

        cousins_children_result = get_children_by_parent_tc(cursor, cousin[1])
        for cousins_child in cousins_children_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, cousins_child[1])
            write_person_info(writer, cousins_child, prefix + f"{cousin[2]} {cousin[3]}'in Çocuğu", gsm_data)

def process_tc_number(tc_no):
    db_config, gsm_config = read_config()
    cnx = connect_to_database(db_config)
    if not cnx:
        messagebox.showerror("Hata", "Veritabanına bağlanılamadı.")
        return

    gsm_cnx = connect_to_database(gsm_config)
    if not gsm_cnx:
        messagebox.showerror("Hata", "GSM veritabanına bağlanılamadı.")
        cnx.close()
        return

    cursor = cnx.cursor()
    gsm_cursor = gsm_cnx.cursor()

    main_person = get_family_member_by_tc(cursor, tc_no)
    if main_person:
        filename = f"./index/{main_person[2]}_{main_person[3]}.csv"
        if os.path.exists(filename) and not messagebox.askyesno("Dosya Var", f"{filename} zaten var. Üzerine yazmak istiyor musunuz?"):
            messagebox.showinfo("İptal", "İşlem iptal edildi.")
            return

        with open(filename, "w", encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Kategori", "TC", "Adı", "Soyadı", "Doğum Tarihi", "Nufus İli", "Nufus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk", "GSM"])

            for family_type, tc in [("Kendi Sülalesi", tc_no), ("Annesinin Sülalesi", main_person[8]), ("Babasının Sülalesi", main_person[10])]:
                writer.writerow([])
                writer.writerow([family_type])
                process_family_tree(cursor, gsm_cursor, tc, writer, "")

        messagebox.showinfo("Başarılı", f"Veriler {filename} dosyasına kaydedildi.")
    else:
        messagebox.showinfo("Bulunamadı", "Girilen TC Kimlik Numarası ile eşleşen kayıt bulunamadı.")

    cnx.close()
    gsm_cnx.close()

def main():
    root = tk.Tk()
    root.title("Family Tree")

    tk.Label(root, text="TC Kimlik Numarası:").pack(pady=10)
    entry = tk.Entry(root, width=30)
    entry.pack(pady=10)
    tk.Button(root, text="Oluştur", command=lambda: process_tc_number(entry.get())).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
