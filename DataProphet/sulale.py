import mysql.connector
import csv
from mysql.connector import Error

def write_person_info(writer, person, category):
    writer.writerow([category] + [str(value) for value in person[1:]])

def connect_to_database():
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
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Error as e:
        print(f"Sorgu çalıştırılırken hata oluştu: {e}")
        return None

# MySQL bağlantısı oluşturma
cnx = connect_to_database()
if not cnx:
    exit(1)

cursor = cnx.cursor()

tc_no = "12345"  # kişi tc si buraya
query = "SELECT * FROM `101m` WHERE TC = %s"
result = execute_query(cursor, query, (tc_no,))

if result:
    result = result[0]
    # Ana kayıt kişisinin adı ve soyadını al ve dosya adını oluştur
    main_person_name = f"{result[2]}_{result[3]}"
    filename = f"{main_person_name}.csv"

    with open(filename, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Kategori", "TC", "Adı", "Soyadı", "Doğum Tarihi", "Nufus İli", "Nufus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk"])

        # Ana kayıt
        write_person_info(writer, result, "Ana Kayıt")

        # Anne bilgileri
        anne_tc = result[8]
        query = "SELECT * FROM `101m` WHERE TC = %s"
        anne_result = execute_query(cursor, query, (anne_tc,))
        if anne_result:
            write_person_info(writer, anne_result[0], "Anne")

        # Baba bilgileri
        baba_tc = result[10]
        query = "SELECT * FROM `101m` WHERE TC = %s"
        baba_result = execute_query(cursor, query, (baba_tc,))
        if baba_result:
            write_person_info(writer, baba_result[0], "Baba")

        # Çocukları
        query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
        cocuklari_result = execute_query(cursor, query, (result[1], result[1]))
        if cocuklari_result:
            for cocuk in cocuklari_result:
                write_person_info(writer, cocuk, "Çocuk")

                # Torunları
                query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
                torunlari_result = execute_query(cursor, query, (cocuk[1], cocuk[1]))
                if torunlari_result:
                    for torun in torunlari_result:
                        write_person_info(writer, torun, f"{cocuk[2]} {cocuk[3]}'in Çocuğu")

        # Kardeşleri
        query = "SELECT * FROM `101m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s"
        kardesleri_result = execute_query(cursor, query, (anne_tc, baba_tc, tc_no))
        if kardesleri_result:
            for kardes in kardesleri_result:
                write_person_info(writer, kardes, "Kardeşi")

                # Yeğenleri
                query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
                yegenleri_result = execute_query(cursor, query, (kardes[1], kardes[1]))
                if yegenleri_result:
                    for yegen in yegenleri_result:
                        write_person_info(writer, yegen, "Yeğeni (Kardeşinin Çocuğu)")

                        # Yeğenin Çocuğu
                        query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
                        yegenin_cocugu_result = execute_query(cursor, query, (yegen[1], yegen[1]))
                        if yegenin_cocugu_result:
                            for yegenin_cocugu in yegenin_cocugu_result:
                                write_person_info(writer, yegenin_cocugu, f"{yegen[2]} {yegen[3]}'in Çocuğu")

        # Dayı/Teyze ve onların çocukları (Kuzenler)
        query = "SELECT * FROM `101m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s"
        dayı_teyze_result = execute_query(cursor, query, (anne_result[0][8], anne_result[0][10], anne_result[0][1]))
        dayı_teyze_cocuklari_result = []
        if dayı_teyze_result:
            for dayı_teyze in dayı_teyze_result:
                write_person_info(writer, dayı_teyze, "----Dayı/Teyze")

                query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
                dayı_teyze_cocuklari = execute_query(cursor, query, (dayı_teyze[1], dayı_teyze[1]))
                if dayı_teyze_cocuklari:
                    for atcocuk in dayı_teyze_cocuklari:
                        write_person_info(writer, atcocuk, "--Kuzen ")
                        dayı_teyze_cocuklari_result.append(atcocuk)

                        # Kuzenin Çocuğu
                        query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
                        kuzenin_cocugu_result = execute_query(cursor, query, (atcocuk[1], atcocuk[1]))
                        if kuzenin_cocugu_result:
                            for kuzenin_cocugu in kuzenin_cocugu_result:
                                write_person_info(writer, kuzenin_cocugu, f"{atcocuk[2]} {atcocuk[3]}'in Çocuğu")

        # Amca/Hala ve onların çocukları (Kuzenler)
        query = "SELECT * FROM `101m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s"
        amca_hala_result = execute_query(cursor, query, (baba_result[0][8], baba_result[0][10], baba_result[0][1]))
        amca_hala_cocuklari_result = []
        if amca_hala_result:
            for amca_hala in amca_hala_result:
                write_person_info(writer, amca_hala, "----Amca/Hala")

                query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
                amca_hala_cocuklari = execute_query(cursor, query, (amca_hala[1], amca_hala[1]))
                if amca_hala_cocuklari:
                    for btcocuk in amca_hala_cocuklari:
                        write_person_info(writer, btcocuk, "--Kuzen ")
                        amca_hala_cocuklari_result.append(btcocuk)

                        # Kuzenin Çocuğu
                        query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
                        kuzenin_cocugu_result = execute_query(cursor, query, (btcocuk[1], btcocuk[1]))
                        if kuzenin_cocugu_result:
                            for kuzenin_cocugu in kuzenin_cocugu_result:
                                write_person_info(writer, kuzenin_cocugu, f"{btcocuk[2]} {btcocuk[3]}'in Çocuğu")



            # Dayı/Teyze ve Amca/Hala TC'lerini bir listeye topla
            dayı_teyze_amca_hala_tc_list = []
            if dayı_teyze_result:
                dayı_teyze_amca_hala_tc_list.extend([dayı_teyze[1] for dayı_teyze in dayı_teyze_result])
            if amca_hala_result:
                dayı_teyze_amca_hala_tc_list.extend([amca_hala[1] for amca_hala in amca_hala_result])

            # Tüm kuzenleri tek bir sorguda al
            if dayı_teyze_amca_hala_tc_list:
                query = "SELECT * FROM `101m` WHERE ANNETC IN (%s) OR BABATC IN (%s)" % (','.join(['%s'] * len(dayı_teyze_amca_hala_tc_list)), ','.join(['%s'] * len(dayı_teyze_amca_hala_tc_list)))
                kuzenleri_result = execute_query(cursor, query, dayı_teyze_amca_hala_tc_list + dayı_teyze_amca_hala_tc_list)
            else:
                kuzenleri_result = []

            # Summary
            summary_data = {
                "Amca/Hala Sayısı": len(amca_hala_result) if amca_hala_result else 0,
                "Dayı/Teyze Sayısı": len(dayı_teyze_result) if dayı_teyze_result else 0,
                "Kuzen Sayısı": len(kuzenleri_result) if kuzenleri_result else 0,
                "Kardeş Sayısı": len(kardesleri_result) if kardesleri_result else 0,
                "Yeğen Sayısı": len(yegenleri_result) if yegenleri_result else 0,
                "Çocuk Sayısı": len(cocuklari_result) if cocuklari_result else 0
            }


            writer.writerow([])
            writer.writerow(["Özet"])
            for key, value in summary_data.items():
                writer.writerow([key, value])

else:
    print("Bulunamadı")

cnx.close()
