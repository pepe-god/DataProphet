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

def write_person_info(writer, person, category, gsm_data=None):
    writer.writerow([category] + [str(value) for value in person[1:]] + ([gsm_data] if gsm_data else []))

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

def write_summary(writer, summary_data):
    writer.writerow([])
    writer.writerow(["Özet"])
    for key, value in summary_data.items():
        writer.writerow([key, value])

def process_family_tree(cursor, gsm_cursor, tc_no, writer, prefix=""):
    main_person = get_family_member_by_tc(cursor, tc_no)
    if not main_person:
        return

    gsm_data = get_gsm_data_by_tc(gsm_cursor, tc_no)
    write_person_info(writer, main_person, prefix + "Ana Kayıt", gsm_data)

    # Anne bilgileri
    anne_tc = main_person[8]
    anne_result = get_family_member_by_tc(cursor, anne_tc)
    if anne_result:
        gsm_data = get_gsm_data_by_tc(gsm_cursor, anne_tc)
        write_person_info(writer, anne_result, prefix + "Anne", gsm_data)

        # Anne'nin ebeveynleri (Büyükanne ve Büyükbaba)
        anne_anne_tc = anne_result[8]
        anne_baba_tc = anne_result[10]
        anne_anne_result = get_family_member_by_tc(cursor, anne_anne_tc)
        anne_baba_result = get_family_member_by_tc(cursor, anne_baba_tc)
        if anne_anne_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, anne_anne_tc)
            write_person_info(writer, anne_anne_result, prefix + "Büyükanne (Anne'nin Anne)", gsm_data)
        if anne_baba_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, anne_baba_tc)
            write_person_info(writer, anne_baba_result, prefix + "Büyükbaba (Anne'nin Baba)", gsm_data)

    # Baba bilgileri
    baba_tc = main_person[10]
    baba_result = get_family_member_by_tc(cursor, baba_tc)
    if baba_result:
        gsm_data = get_gsm_data_by_tc(gsm_cursor, baba_tc)
        write_person_info(writer, baba_result, prefix + "Baba", gsm_data)

        # Baba'nın ebeveynleri (Büyükanne ve Büyükbaba)
        baba_anne_tc = baba_result[8]
        baba_baba_tc = baba_result[10]
        baba_anne_result = get_family_member_by_tc(cursor, baba_anne_tc)
        baba_baba_result = get_family_member_by_tc(cursor, baba_baba_tc)
        if baba_anne_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, baba_anne_tc)
            write_person_info(writer, baba_anne_result, prefix + "Büyükanne (Baba'nın Anne)", gsm_data)
        if baba_baba_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, baba_baba_tc)
            write_person_info(writer, baba_baba_result, prefix + "Büyükbaba (Baba'nın Baba)", gsm_data)

    # Çocukları
    cocuklari_result = get_children_by_parent_tc(cursor, main_person[1])
    if cocuklari_result:
        for cocuk in cocuklari_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, cocuk[1])
            write_person_info(writer, cocuk, prefix + "-Çocuk", gsm_data)

            # Torunları
            torunlari_result = get_children_by_parent_tc(cursor, cocuk[1])
            if torunlari_result:
                for torun in torunlari_result:
                    gsm_data = get_gsm_data_by_tc(gsm_cursor, torun[1])
                    write_person_info(writer, torun, prefix + f"{cocuk[2]} {cocuk[3]}'in Çocuğu", gsm_data)

    # Kardeşleri
    kardesleri_result = get_siblings_by_parent_tc(cursor, anne_tc, baba_tc, tc_no)
    yegenleri_count = 0
    if kardesleri_result:
        for kardes in kardesleri_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, kardes[1])
            write_person_info(writer, kardes, prefix + "--Kardeşi", gsm_data)

            # Yeğenleri
            yegenleri_result = get_children_by_parent_tc(cursor, kardes[1])
            if yegenleri_result:
                yegenleri_count += len(yegenleri_result)
                for yegen in yegenleri_result:
                    gsm_data = get_gsm_data_by_tc(gsm_cursor, yegen[1])
                    write_person_info(writer, yegen, prefix + "Yeğeni", gsm_data)

                    # Yeğenin Çocuğu
                    yegenin_cocugu_result = get_children_by_parent_tc(cursor, yegen[1])
                    if yegenin_cocugu_result:
                        for yegenin_cocugu in yegenin_cocugu_result:
                            gsm_data = get_gsm_data_by_tc(gsm_cursor, yegenin_cocugu[1])
                            write_person_info(writer, yegenin_cocugu, prefix + f"{yegen[2]} {yegen[3]}'in Çocuğu", gsm_data)

    # Dayı/Teyze ve Amca/Hala TC'lerini bir listeye topla
    dayı_teyze_amca_hala_tc_list = []
    dayı_teyze_result = []
    amca_hala_result = []
    if anne_result:
        dayı_teyze_result = get_siblings_by_parent_tc(cursor, anne_result[8], anne_result[10], anne_result[1])
        if dayı_teyze_result:
            dayı_teyze_amca_hala_tc_list.extend([dayı_teyze[1] for dayı_teyze in dayı_teyze_result])
            for dayı_teyze in dayı_teyze_result:
                gsm_data = get_gsm_data_by_tc(gsm_cursor, dayı_teyze[1])
                write_person_info(writer, dayı_teyze, prefix + "---Dayı/Teyze", gsm_data)
    if baba_result:
        amca_hala_result = get_siblings_by_parent_tc(cursor, baba_result[8], baba_result[10], baba_result[1])
        if amca_hala_result:
            dayı_teyze_amca_hala_tc_list.extend([amca_hala[1] for amca_hala in amca_hala_result])
            for amca_hala in amca_hala_result:
                gsm_data = get_gsm_data_by_tc(gsm_cursor, amca_hala[1])
                write_person_info(writer, amca_hala, prefix + "---Amca/Hala", gsm_data)

    # Tüm kuzenleri tek bir sorguda al
    kuzenleri_result = get_cousins_by_parent_tc_list(cursor, dayı_teyze_amca_hala_tc_list)
    if kuzenleri_result:
        for kuzen in kuzenleri_result:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, kuzen[1])
            write_person_info(writer, kuzen, prefix + "Kuzen", gsm_data)

            # Kuzenin Çocukları
            kuzen_cocuklari_result = get_children_by_parent_tc(cursor, kuzen[1])
            if kuzen_cocuklari_result:
                for kuzen_cocugu in kuzen_cocuklari_result:
                    gsm_data = get_gsm_data_by_tc(gsm_cursor, kuzen_cocugu[1])
                    write_person_info(writer, kuzen_cocugu, prefix + f"{kuzen[2]} {kuzen[3]}'in Çocuğu", gsm_data)

    return {
        "Kuzen Sayısı": len(kuzenleri_result) if kuzenleri_result else 0,
        "Kardeş Sayısı": len(kardesleri_result) if kardesleri_result else 0,
        "Yeğen Sayısı": yegenleri_count,
        "Çocuk Sayısı": len(cocuklari_result) if cocuklari_result else 0,
        "Amca/Hala Sayısı": len(amca_hala_result) if amca_hala_result else 0,
        "Dayı/Teyze Sayısı": len(dayı_teyze_result) if dayı_teyze_result else 0,
        "Kuzen Çocukları Sayısı": sum([len(get_children_by_parent_tc(cursor, kuzen[1])) for kuzen in kuzenleri_result]) if kuzenleri_result else 0,
    }

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
        main_person_name = f"{main_person[2]}_{main_person[3]}"
        filename = f"{main_person_name}.csv"

        if os.path.exists(filename):
            if messagebox.askyesno("Dosya Var", f"{filename} zaten var. Üzerine yazmak istiyor musunuz?"):
                pass
            else:
                messagebox.showinfo("İptal", "İşlem iptal edildi.")
                cnx.close()
                gsm_cnx.close()
                return

        with open(filename, "w", encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Kategori", "TC", "Adı", "Soyadı", "Doğum Tarihi", "Nufus İli", "Nufus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk", "GSM"])

            # Ana kişinin kendi sülalesi
            writer.writerow([])
            writer.writerow([f"Kendi Sülalesi"])
            summary_data_kendi = process_family_tree(cursor, gsm_cursor, tc_no, writer, f"")
            write_summary(writer, summary_data_kendi)

            # Ana kişinin annesinin sülalesi
            anne_tc = main_person[8]
            if anne_tc:
                writer.writerow([])
                writer.writerow([f"Annesinin Sülalesi"])
                summary_data_anne = process_family_tree(cursor, gsm_cursor, anne_tc, writer, f"")
                write_summary(writer, summary_data_anne)

            # Ana kişinin babasının sülalesi
            baba_tc = main_person[10]
            if baba_tc:
                writer.writerow([])
                writer.writerow([f"Babasının Sülalesi"])
                summary_data_baba = process_family_tree(cursor, gsm_cursor, baba_tc, writer, f"")
                write_summary(writer, summary_data_baba)

        messagebox.showinfo("Başarılı", f"Veriler {filename} dosyasına kaydedildi.")
    else:
        messagebox.showinfo("Bulunamadı", "Girilen TC Kimlik Numarası ile eşleşen kayıt bulunamadı.")

    cnx.close()
    gsm_cnx.close()

def main():
    root = tk.Tk()
    root.title("Family Tree")

    label = tk.Label(root, text="TC Kimlik Numarası:")
    label.pack(pady=10)

    entry = tk.Entry(root, width=30)
    entry.pack(pady=10)

    button = tk.Button(root, text="Oluştur", command=lambda: process_tc_number(entry.get()))
    button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
