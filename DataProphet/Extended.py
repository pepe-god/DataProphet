import mysql.connector
import csv
import os
import logging
import configparser
from mysql.connector import Error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'DATABASE' not in config:
        logger.error("Config dosyasında 'DATABASE' bölümü bulunamadı.")
        return None
    return config['DATABASE']

def validate_tc(tc_no):
    return len(tc_no) == 11 and tc_no.isdigit()

def write_person_info(writer, person, category):
    writer.writerow([category] + [str(value) for value in person[1:]])

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

def write_summary(writer, summary_data):
    writer.writerow([])
    writer.writerow(["Özet"])
    for key, value in summary_data.items():
        writer.writerow([key, value])

def process_family_tree(cursor, tc_no, writer, prefix=""):
    main_person = get_family_member_by_tc(cursor, tc_no)

    if main_person:
        # Ana kayıt
        write_person_info(writer, main_person, f"{prefix}Ana Kayıt")

        # Anne bilgileri
        anne_tc = main_person[8]
        anne_result = get_family_member_by_tc(cursor, anne_tc)
        if anne_result:
            write_person_info(writer, anne_result, f"{prefix}Anne")

            # Anne'nin ebeveynleri (Büyükanne ve Büyükbaba)
            anne_anne_tc = anne_result[8]
            anne_baba_tc = anne_result[10]
            anne_anne_result = get_family_member_by_tc(cursor, anne_anne_tc)
            anne_baba_result = get_family_member_by_tc(cursor, anne_baba_tc)
            if anne_anne_result:
                write_person_info(writer, anne_anne_result, f"{prefix}Büyükanne (Anne'nin Anne)")
            if anne_baba_result:
                write_person_info(writer, anne_baba_result, f"{prefix}Büyükbaba (Anne'nin Baba)")

        # Baba bilgileri
        baba_tc = main_person[10]
        baba_result = get_family_member_by_tc(cursor, baba_tc)
        if baba_result:
            write_person_info(writer, baba_result, f"{prefix}Baba")

            # Baba'nın ebeveynleri (Büyükanne ve Büyükbaba)
            baba_anne_tc = baba_result[8]
            baba_baba_tc = baba_result[10]
            baba_anne_result = get_family_member_by_tc(cursor, baba_anne_tc)
            baba_baba_result = get_family_member_by_tc(cursor, baba_baba_tc)
            if baba_anne_result:
                write_person_info(writer, baba_anne_result, f"{prefix}Büyükanne (Baba'nın Anne)")
            if baba_baba_result:
                write_person_info(writer, baba_baba_result, f"{prefix}Büyükbaba (Baba'nın Baba)")

        # Çocukları
        cocuklari_result = get_children_by_parent_tc(cursor, main_person[1])
        if cocuklari_result:
            for cocuk in cocuklari_result:
                write_person_info(writer, cocuk, f"{prefix}-Çocuk")

                # Torunları
                torunlari_result = get_children_by_parent_tc(cursor, cocuk[1])
                if torunlari_result:
                    for torun in torunlari_result:
                        write_person_info(writer, torun, f"{prefix}{cocuk[2]} {cocuk[3]}'in Çocuğu")

        # Kardeşleri
        kardesleri_result = get_siblings_by_parent_tc(cursor, anne_tc, baba_tc, tc_no)
        if kardesleri_result:
            for kardes in kardesleri_result:
                write_person_info(writer, kardes, f"{prefix}--Kardeşi")

                # Yeğenleri
                yegenleri_result = get_children_by_parent_tc(cursor, kardes[1])
                if yegenleri_result:
                    for yegen in yegenleri_result:
                        write_person_info(writer, yegen, f"{prefix}Yeğeni")

                        # Yeğenin Çocuğu
                        yegenin_cocugu_result = get_children_by_parent_tc(cursor, yegen[1])
                        if yegenin_cocugu_result:
                            for yegenin_cocugu in yegenin_cocugu_result:
                                write_person_info(writer, yegenin_cocugu, f"{prefix}{yegen[2]} {yegen[3]}'in Çocuğu")

        # Dayı/Teyze ve Amca/Hala TC'lerini bir listeye topla
        dayı_teyze_amca_hala_tc_list = []
        dayı_teyze_result = []
        amca_hala_result = []
        if anne_result:
            dayı_teyze_result = get_siblings_by_parent_tc(cursor, anne_result[8], anne_result[10], anne_result[1])
            if dayı_teyze_result:
                dayı_teyze_amca_hala_tc_list.extend([dayı_teyze[1] for dayı_teyze in dayı_teyze_result])
                for dayı_teyze in dayı_teyze_result:
                    write_person_info(writer, dayı_teyze, f"{prefix}---Dayı/Teyze")
        if baba_result:
            amca_hala_result = get_siblings_by_parent_tc(cursor, baba_result[8], baba_result[10], baba_result[1])
            if amca_hala_result:
                dayı_teyze_amca_hala_tc_list.extend([amca_hala[1] for amca_hala in amca_hala_result])
                for amca_hala in amca_hala_result:
                    write_person_info(writer, amca_hala, f"{prefix}---Amca/Hala")

        # Tüm kuzenleri tek bir sorguda al
        kuzenleri_result = get_cousins_by_parent_tc_list(cursor, dayı_teyze_amca_hala_tc_list)
        if kuzenleri_result:
            for kuzen in kuzenleri_result:
                write_person_info(writer, kuzen, f"{prefix}Kuzen")

                # Kuzenin Çocukları
                kuzen_cocuklari_result = get_children_by_parent_tc(cursor, kuzen[1])
                if kuzen_cocuklari_result:
                    for kuzen_cocugu in kuzen_cocuklari_result:
                        write_person_info(writer, kuzen_cocugu, f"{prefix}{kuzen[2]} {kuzen[3]}'in Çocuğu")

        # Summary
        summary_data = {
            "Kuzen Sayısı": len(kuzenleri_result) if kuzenleri_result else 0,
            "Kardeş Sayısı": len(kardesleri_result) if kardesleri_result else 0,
            "Yeğen Sayısı": sum(len(get_children_by_parent_tc(cursor, kardes[1])) for kardes in kardesleri_result) if kardesleri_result else 0,
            "Çocuk Sayısı": len(cocuklari_result) if cocuklari_result else 0,
            "Amca/Hala Sayısı": len(amca_hala_result) if amca_hala_result else 0,
            "Dayı/Teyze Sayısı": len(dayı_teyze_result) if dayı_teyze_result else 0,
        }

        write_summary(writer, summary_data)

    else:
        logger.info("Bulunamadı")

def main():
    db_config = read_config()
    if not db_config:
        return

    with connect_to_database(db_config) as cnx:
        if not cnx:
            return

        cursor = cnx.cursor()

        while True:
            tc_no = input("TC Kimlik Numarasını Girin: ")
            if validate_tc(tc_no):
                break
            else:
                print("Geçersiz TC Kimlik Numarası. Lütfen tekrar deneyin.")

        main_person = get_family_member_by_tc(cursor, tc_no)

        if main_person:
            main_person_name = f"{main_person[2]}_{main_person[3]}"
            filename = f"{main_person_name}.csv"

            if os.path.exists(filename):
                print(f"{filename} zaten var. Üzerine yazmak istiyor musunuz? (E/H)")
                if input().upper() != "E":
                    print("İşlem iptal edildi.")
                    return

            with open(filename, "w", encoding="utf-8", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Kategori", "TC", "Adı", "Soyadı", "Doğum Tarihi", "Nufus İli", "Nufus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk"])

                # Ana kişinin kendi sülalesi
                writer.writerow([])
                writer.writerow([f"Kendi Sülalesi"])
                process_family_tree(cursor, tc_no, writer, f"")

                # Ana kişinin annesinin sülalesi
                anne_tc = main_person[8]
                if anne_tc:
                    writer.writerow([])
                    writer.writerow([f"Annesinin Sülalesi"])
                    process_family_tree(cursor, anne_tc, writer, f"")

                # Ana kişinin babasının sülalesi
                baba_tc = main_person[10]
                if baba_tc:
                    writer.writerow([])
                    writer.writerow([f"Babasının Sülalesi"])
                    process_family_tree(cursor, baba_tc, writer, f"")

        else:
            logger.info("Bulunamadı")

if __name__ == "__main__":
    main()
