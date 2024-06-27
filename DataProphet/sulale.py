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

tc_no = "12345"  # kişi tc si buraya
query = f"SELECT * FROM `101m` WHERE TC = '{tc_no}'"
cursor.execute(query)
result = cursor.fetchone()

if result:
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
        query = f"SELECT * FROM `101m` WHERE TC = '{anne_tc}'"
        cursor.execute(query)
        anne_result = cursor.fetchone()
        if anne_result:
            write_person_info(writer, anne_result, "Anne")

        # Baba bilgileri
        baba_tc = result[10]
        query = f"SELECT * FROM `101m` WHERE TC = '{baba_tc}'"
        cursor.execute(query)
        baba_result = cursor.fetchone()
        if baba_result:
            write_person_info(writer, baba_result, "Baba")

        # Çocukları
        query = f"SELECT * FROM `101m` WHERE ANNETC = '{result[1]}' OR BABATC = '{result[1]}'"
        cursor.execute(query)
        cocuklari_result = cursor.fetchall()
        if cocuklari_result:
            for cocuk in cocuklari_result:
                write_person_info(writer, cocuk, "Çocuk")

                # Torunları
                query = f"SELECT * FROM `101m` WHERE ANNETC = '{cocuk[1]}' OR BABATC = '{cocuk[1]}'"
                cursor.execute(query)
                torunlari_result = cursor.fetchall()
                if torunlari_result:
                    for torun in torunlari_result:
                        write_person_info(writer, torun, f"{cocuk[2]} {cocuk[3]}'in Çocuğu")

        # Kardeşleri
        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_tc}' OR BABATC = '{baba_tc}') AND TC != '{tc_no}'"
        cursor.execute(query)
        kardesleri_result = cursor.fetchall()
        if kardesleri_result:
            for kardes in kardesleri_result:
                write_person_info(writer, kardes, "Kardeşi")

                # Yeğenleri
                query = f"SELECT * FROM `101m` WHERE ANNETC = '{kardes[1]}' OR BABATC = '{kardes[1]}'"
                cursor.execute(query)
                yegenleri_result = cursor.fetchall()
                if yegenleri_result:
                    for yegen in yegenleri_result:
                        write_person_info(writer, yegen, "Yeğeni (Kardeşinin Çocuğu)")

                        # Yeğenin Çocuğu
                        query = f"SELECT * FROM `101m` WHERE ANNETC = '{yegen[1]}' OR BABATC = '{yegen[1]}'"
                        cursor.execute(query)
                        yegenin_cocugu_result = cursor.fetchall()
                        if yegenin_cocugu_result:
                            for yegenin_cocugu in yegenin_cocugu_result:
                                write_person_info(writer, yegenin_cocugu, f"{yegen[2]} {yegen[3]}'in Çocuğu")

        # Dayı/Teyze ve onların çocukları (Kuzenler)
        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_result[8]}' OR BABATC = '{anne_result[10]}') AND TC != '{anne_result[1]}'"
        cursor.execute(query)
        dayı_teyze_result = cursor.fetchall()
        dayı_teyze_cocuklari_result = []
        if dayı_teyze_result:
            for dayı_teyze in dayı_teyze_result:
                write_person_info(writer, dayı_teyze, "----Dayı/Teyze")

                query = f"SELECT * FROM `101m` WHERE ANNETC = '{dayı_teyze[1]}' OR BABATC = '{dayı_teyze[1]}'"
                cursor.execute(query)
                dayı_teyze_cocuklari = cursor.fetchall()
                if dayı_teyze_cocuklari:
                    for atcocuk in dayı_teyze_cocuklari:
                        write_person_info(writer, atcocuk, "--Kuzen ")
                        dayı_teyze_cocuklari_result.append(atcocuk)

                        # Kuzenin Çocuğu
                        query = f"SELECT * FROM `101m` WHERE ANNETC = '{atcocuk[1]}' OR BABATC = '{atcocuk[1]}'"
                        cursor.execute(query)
                        kuzenin_cocugu_result = cursor.fetchall()
                        if kuzenin_cocugu_result:
                            for kuzenin_cocugu in kuzenin_cocugu_result:
                                write_person_info(writer, kuzenin_cocugu, f"{atcocuk[2]} {atcocuk[3]}'in Çocuğu")

        # Amca/Hala ve onların çocukları (Kuzenler)
        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{baba_result[8]}' OR BABATC = '{baba_result[10]}') AND TC != '{baba_result[1]}'"
        cursor.execute(query)
        amca_hala_result = cursor.fetchall()
        amca_hala_cocuklari_result = []
        if amca_hala_result:
            for amca_hala in amca_hala_result:
                write_person_info(writer, amca_hala, "----Amca/Hala")

                query = f"SELECT * FROM `101m` WHERE ANNETC = '{amca_hala[1]}' OR BABATC = '{amca_hala[1]}'"
                cursor.execute(query)
                amca_hala_cocuklari = cursor.fetchall()
                if amca_hala_cocuklari:
                    for btcocuk in amca_hala_cocuklari:
                        write_person_info(writer, btcocuk, "--Kuzen ")
                        amca_hala_cocuklari_result.append(btcocuk)

                        # Kuzenin Çocuğu
                        query = f"SELECT * FROM `101m` WHERE ANNETC = '{btcocuk[1]}' OR BABATC = '{btcocuk[1]}'"
                        cursor.execute(query)
                        kuzenin_cocugu_result = cursor.fetchall()
                        if kuzenin_cocugu_result:
                            for kuzenin_cocugu in kuzenin_cocugu_result:
                                write_person_info(writer, kuzenin_cocugu, f"{btcocuk[2]} {btcocuk[3]}'in Çocuğu")

            # Summary
            summary_data = {
                "Amca/Hala Sayısı": len(amca_hala_result) if amca_hala_result else 0,
                "Dayı/Teyze Sayısı": len(dayı_teyze_result) if dayı_teyze_result else 0,
                "Kuzen Sayısı": len(dayı_teyze_cocuklari_result) + len(amca_hala_cocuklari_result),
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
