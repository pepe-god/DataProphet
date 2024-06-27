import mysql.connector
import csv
import os
from mysql.connector import Error

def write_person_info(writer, person, category):
    """Kişi bilgilerini CSV dosyasına yazar."""
    writer.writerow([category] + [str(value) for value in person[1:]])

def connect_to_database():
    """Veritabanına bağlanır."""
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="101m"
        )
        return cnx
    except Error as e:
        print(f"Veritabanına bağlanırken hata oluştu: {e}")
        return None

def execute_query(cursor, query, params=None):
    """Veritabanı sorgusu çalıştırır ve sonuçları döndürür."""
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Error as e:
        print(f"Sorgu çalıştırılırken hata oluştu: {e}")
        return None

def fetch_family_member(cursor, tc_no):
    """Belirtilen TC kimlik numarasına sahip aile üyesini getirir."""
    query = "SELECT * FROM `101m` WHERE TC = %s"
    result = execute_query(cursor, query, (tc_no,))
    return result[0] if result else None

def fetch_children(cursor, parent_tc):
    """Belirtilen ebeveyn TC kimlik numarasına sahip çocukları getirir."""
    query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
    return execute_query(cursor, query, (parent_tc, parent_tc))

def fetch_siblings(cursor, anne_tc, baba_tc, tc_no):
    """Belirtilen anne ve baba TC kimlik numaralarına sahip kardeşleri getirir."""
    query = "SELECT * FROM `101m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s"
    return execute_query(cursor, query, (anne_tc, baba_tc, tc_no))

def fetch_cousins(cursor, parent_tc_list):
    """Belirtilen ebeveyn TC kimlik numaralarına sahip kuzenleri getirir."""
    if parent_tc_list:
        query = "SELECT * FROM `101m` WHERE ANNETC IN (%s) OR BABATC IN (%s)" % (','.join(['%s'] * len(parent_tc_list)), ','.join(['%s'] * len(parent_tc_list)))
        return execute_query(cursor, query, parent_tc_list + parent_tc_list)
    return []

def write_summary(writer, summary_data):
    """Özet bilgilerini CSV dosyasına yazar."""
    writer.writerow([])
    writer.writerow(["Özet"])
    for key, value in summary_data.items():
        writer.writerow([key, value])

# MySQL bağlantısı oluşturma
cnx = connect_to_database()
if not cnx:
    exit(1)

cursor = cnx.cursor()

tc_no = input("TC Kimlik Numarasını Girin: ")  # kişi tc si buraya
main_person = fetch_family_member(cursor, tc_no)

if main_person:
    main_person_name = f"{main_person[2]}_{main_person[3]}"
    filename = f"{main_person_name}.csv"

    if os.path.exists(filename):
        print(f"{filename} zaten var. Üzerine yazmak istiyor musunuz? (E/H)")
        if input().upper() != "E":
            print("İşlem iptal edildi.")
            cnx.close()
            exit(1)

    with open(filename, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Kategori", "TC", "Adı", "Soyadı", "Doğum Tarihi", "Nufus İli", "Nufus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk"])

        # Ana kayıt
        write_person_info(writer, main_person, "Ana Kayıt")

        # Anne bilgileri
        anne_tc = main_person[8]
        anne_result = fetch_family_member(cursor, anne_tc)
        if anne_result:
            write_person_info(writer, anne_result, "Anne")

        # Baba bilgileri
        baba_tc = main_person[10]
        baba_result = fetch_family_member(cursor, baba_tc)
        if baba_result:
            write_person_info(writer, baba_result, "Baba")

        # Çocukları
        cocuklari_result = fetch_children(cursor, main_person[1])
        if cocuklari_result:
            for cocuk in cocuklari_result:
                write_person_info(writer, cocuk, "-Çocuk")

                # Torunları
                torunlari_result = fetch_children(cursor, cocuk[1])
                if torunlari_result:
                    for torun in torunlari_result:
                        write_person_info(writer, torun, f"{cocuk[2]} {cocuk[3]}'in Çocuğu")

        # Kardeşleri
        kardesleri_result = fetch_siblings(cursor, anne_tc, baba_tc, tc_no)
        if kardesleri_result:
            for kardes in kardesleri_result:
                write_person_info(writer, kardes, "--Kardeşi")

                # Yeğenleri
                yegenleri_result = fetch_children(cursor, kardes[1])
                if yegenleri_result:
                    for yegen in yegenleri_result:
                        write_person_info(writer, yegen, "Yeğeni (Kardeşinin Çocuğu)")

                        # Yeğenin Çocuğu
                        yegenin_cocugu_result = fetch_children(cursor, yegen[1])
                        if yegenin_cocugu_result:
                            for yegenin_cocugu in yegenin_cocugu_result:
                                write_person_info(writer, yegenin_cocugu, f"{yegen[2]} {yegen[3]}'in Çocuğu")

        # Dayı/Teyze ve Amca/Hala TC'lerini bir listeye topla
        dayı_teyze_amca_hala_tc_list = []
        dayı_teyze_result = []
        amca_hala_result = []
        if anne_result:
            dayı_teyze_result = fetch_siblings(cursor, anne_result[8], anne_result[10], anne_result[1])
            if dayı_teyze_result:
                dayı_teyze_amca_hala_tc_list.extend([dayı_teyze[1] for dayı_teyze in dayı_teyze_result])
                for dayı_teyze in dayı_teyze_result:
                    write_person_info(writer, dayı_teyze, "---Dayı/Teyze")
        if baba_result:
            amca_hala_result = fetch_siblings(cursor, baba_result[8], baba_result[10], baba_result[1])
            if amca_hala_result:
                dayı_teyze_amca_hala_tc_list.extend([amca_hala[1] for amca_hala in amca_hala_result])
                for amca_hala in amca_hala_result:
                    write_person_info(writer, amca_hala, "---Amca/Hala")

        # Tüm kuzenleri tek bir sorguda al
        kuzenleri_result = fetch_cousins(cursor, dayı_teyze_amca_hala_tc_list)
        if kuzenleri_result:
            for kuzen in kuzenleri_result:
                write_person_info(writer, kuzen, "Kuzen")

                # Kuzenin Çocukları
                kuzen_cocuklari_result = fetch_children(cursor, kuzen[1])
                if kuzen_cocuklari_result:
                    for kuzen_cocugu in kuzen_cocuklari_result:
                        write_person_info(writer, kuzen_cocugu, f"{kuzen[2]} {kuzen[3]}'in Çocuğu")

        # Summary
        summary_data = {
            "Kuzen Sayısı": len(kuzenleri_result) if kuzenleri_result else 0,
            "Kardeş Sayısı": len(kardesleri_result) if kardesleri_result else 0,
            "Yeğen Sayısı": len(yegenleri_result) if yegenleri_result else 0,
            "Çocuk Sayısı": len(cocuklari_result) if cocuklari_result else 0,
            "Amca/Hala Sayısı": len(amca_hala_result) if amca_hala_result else 0,
            "Dayı/Teyze Sayısı": len(dayı_teyze_result) if dayı_teyze_result else 0,
        }

        write_summary(writer, summary_data)

else:
    print("Bulunamadı")

cnx.close()