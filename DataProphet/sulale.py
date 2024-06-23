import mysql.connector
import csv

def write_person_info(writer, person, category):
    writer.writerow([category] + [str(value) for value in person[1:]])

# MySQL bağlantısı oluşturma
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="101m"
)
cursor = cnx.cursor()

tc_no = "11223344"  # kişi tc si buraya
query = f"SELECT * FROM `101m` WHERE TC = '{tc_no}'"
cursor.execute(query)
result = cursor.fetchone()

if result:
    with open("sulale.csv", "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Kategori", "TC", "Adı", "Soyadı", "Doğum Tarihi", "Nufus İli", "Nufus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk"])

        write_person_info(writer, result, "Bulunan kayıt")

        anne_tc = result[8]
        query = f"SELECT * FROM `101m` WHERE TC = '{anne_tc}'"
        cursor.execute(query)
        anne_result = cursor.fetchone()
        if anne_result:
            write_person_info(writer, anne_result, "Anne ")

        baba_tc = result[10]
        query = f"SELECT * FROM `101m` WHERE TC = '{baba_tc}'"
        cursor.execute(query)
        baba_result = cursor.fetchone()
        if baba_result:
            write_person_info(writer, baba_result, "Baba ")

        query = f"SELECT * FROM `101m` WHERE ANNETC = '{result[1]}' OR BABATC = '{result[1]}'"
        cursor.execute(query)
        cocuklari_result = cursor.fetchall()
        if cocuklari_result:
            for cocuk in cocuklari_result:
                write_person_info(writer, cocuk, "Çocuklarının ")

        if cocuklari_result:
            for cocuk in cocuklari_result:
                query = f"SELECT * FROM `101m` WHERE ANNETC = '{cocuk[1]}' OR BABATC = '{cocuk[1]}'"
                cursor.execute(query)
                torunlari_result = cursor.fetchall()
                if torunlari_result:
                    for torun in torunlari_result:
                        write_person_info(writer, torun, "Torunlarının ")

        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_tc}' OR BABATC = '{baba_tc}') AND TC != '{tc_no}'"
        cursor.execute(query)
        kardesleri_result = cursor.fetchall()
        if kardesleri_result:
            for kardes in kardesleri_result:
                write_person_info(writer, kardes, "Kardeşleri ")

                query = f"SELECT * FROM `101m` WHERE ANNETC = '{kardes[1]}' OR BABATC = '{kardes[1]}'"
                cursor.execute(query)
                yegenleri_result = cursor.fetchall()
                if yegenleri_result:
                    for yegen in yegenleri_result:
                        write_person_info(writer, yegen, "Yeğen ")

        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_result[8]}' OR BABATC = '{anne_result[10]}') AND TC != '{anne_result[1]}'"
        cursor.execute(query)
        dayı_teyze_result = cursor.fetchall()
        if dayı_teyze_result:
            for dayı_teyze in dayı_teyze_result:
                write_person_info(writer, dayı_teyze, "Dayı/Teyze ")

                query = f"SELECT * FROM `101m` WHERE ANNETC = '{dayı_teyze[1]}' OR BABATC = '{dayı_teyze[1]}'"
                cursor.execute(query)
                dayı_teyze_cocuklari_result = cursor.fetchall()
                if dayı_teyze_cocuklari_result:
                    for atcocuk in dayı_teyze_cocuklari_result:
                        write_person_info(writer, atcocuk, "Anne.T Kuzen ")

        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{baba_result[8]}' OR BABATC = '{baba_result[10]}') AND TC != '{baba_result[1]}'"
        cursor.execute(query)
        amca_hala_result = cursor.fetchall()
        if amca_hala_result:
            for amca_hala in amca_hala_result:
                write_person_info(writer, amca_hala, "Amca/Hala ")

                query = f"SELECT * FROM `101m` WHERE ANNETC = '{amca_hala[1]}' OR BABATC = '{amca_hala[1]}'"
                cursor.execute(query)
                amca_hala_cocuklari_result = cursor.fetchall()
                if amca_hala_cocuklari_result:
                    for btcocuk in amca_hala_cocuklari_result:
                        write_person_info(writer, btcocuk, "Baba.T Kuzen ")
else:
    print("Bulunamadı")

cnx.close()
