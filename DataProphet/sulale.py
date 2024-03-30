import mysql.connector
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="101m"
)
cursor = cnx.cursor()
tc_no = "1122334455"  # kişi tc si buraya
query = f"SELECT * FROM `101m` WHERE TC = '{tc_no}'"
cursor.execute(query)
result = cursor.fetchone()
if result:
    with open("sulale.txt", "w", encoding="utf-8") as file:
        file.write("Bulunan kayıt:\n")
        file.write(f"TC: {result[1]}\t")
        file.write(f"Adı: {result[2]}\t")
        file.write(f"Soyadı: {result[3]}\t")
        file.write(f"Doğum Tarihi: {result[4]}\t")
        file.write(f"Nufus İli: {result[5]}\t")
        file.write(f"Nufus İlçesi: {result[6]}\t")
        file.write(f"Anne Adı: {result[7]}\t")
        file.write(f"Anne TC: {result[8]}\t")
        file.write(f"Baba Adı: {result[9]}\t")
        file.write(f"Baba TC: {result[10]}\t")
        file.write(f"Uyruk: {result[11]}\n")

        anne_tc = result[8]
        query = f"SELECT * FROM `101m` WHERE TC = '{anne_tc}'"
        cursor.execute(query)
        anne_result = cursor.fetchone()

        if anne_result:
            file.write("\nAnne bilgileri:\n")
            file.write(f"TC: {anne_result[1]}\t")
            file.write(f"Adı: {anne_result[2]}\t")
            file.write(f"Soyadı: {anne_result[3]}\t")
            file.write(f"Doğum Tarihi: {anne_result[4]}\t")
            file.write(f"Nufus İli: {anne_result[5]}\t")
            file.write(f"Nufus İlçesi: {anne_result[6]}\t")
            file.write(f"Anne Adı: {anne_result[7]}\t")
            file.write(f"Anne TC: {anne_result[8]}\t")
            file.write(f"Baba Adı: {anne_result[9]}\t")
            file.write(f"Baba TC: {anne_result[10]}\t")
            file.write(f"Uyruk: {anne_result[11]}\n")
        else:
            file.write("\nAnne bilgisi bulunamadı.\n")

        baba_tc = result[10] 
        query = f"SELECT * FROM `101m` WHERE TC = '{baba_tc}'"
        cursor.execute(query)
        baba_result = cursor.fetchone()

        if baba_result:
            file.write("\nBaba bilgileri:\n")
            file.write(f"TC: {baba_result[1]}\t")
            file.write(f"Adı: {baba_result[2]}\t")
            file.write(f"Soyadı: {baba_result[3]}\t")
            file.write(f"Doğum Tarihi: {baba_result[4]}\t")
            file.write(f"Nufus İli: {baba_result[5]}\t")
            file.write(f"Nufus İlçesi: {baba_result[6]}\t")
            file.write(f"Anne Adı: {baba_result[7]}\t")
            file.write(f"Anne TC: {baba_result[8]}\t")
            file.write(f"Baba Adı: {baba_result[9]}\t")
            file.write(f"Baba TC: {baba_result[10]}\t")
            file.write(f"Uyruk: {baba_result[11]}\n")
        else:
            file.write("\nBaba bilgisi bulunamadı.\n")

        query = f"SELECT * FROM `101m` WHERE ANNETC = '{result[1]}' OR BABATC = '{result[1]}'"
        cursor.execute(query)
        cocuklari_result = cursor.fetchall()

        if cocuklari_result:
            cocuklar_listesi = []
            file.write("\nÇocuklarının bilgileri:\n")
            for cocuk in cocuklari_result:
                cocuklar_listesi.append(cocuk)
                file.write(f"TC: {cocuk[1]}\t")
                file.write(f"Adı: {cocuk[2]}\t")
                file.write(f"Soyadı: {cocuk[3]}\t")
                file.write(f"Doğum Tarihi: {cocuk[4]}\t")
                file.write(f"Nufus İli: {cocuk[5]}\t")
                file.write(f"Nufus İlçesi: {cocuk[6]}\t")
                file.write(f"Anne Adı: {cocuk[7]}\t")
                file.write(f"Anne TC: {cocuk[8]}\t")
                file.write(f"Baba Adı: {cocuk[9]}\t")
                file.write(f"Baba TC: {cocuk[10]}\t")
                file.write(f"Uyruk: {cocuk[11]}\n")
        else:
            file.write("Kişinin Çocuklarının bilgileri bulunamadı.\n")

        if 'cocuklar_listesi' in locals():
            for cocuk in cocuklar_listesi:
                query = f"SELECT * FROM `101m` WHERE ANNETC = '{cocuk[1]}' OR BABATC = '{cocuk[1]}'"
                cursor.execute(query)
                torunlari_result = cursor.fetchall()

                if torunlari_result:
                    file.write("\nTorunlarının bilgileri:\n")
                    for torun in torunlari_result:
                        file.write(f"TC: {torun[1]}\t")
                        file.write(f"Adı: {torun[2]}\t")
                        file.write(f"Soyadı: {torun[3]}\t")
                        file.write(f"Doğum Tarihi: {torun[4]}\t")
                        file.write(f"Nufus İli: {torun[5]}\t")
                        file.write(f"Nufus İlçesi: {torun[6]}\t")
                        file.write(f"Anne Adı: {torun[7]}\t")
                        file.write(f"Anne TC: {torun[8]}\t")
                        file.write(f"Baba Adı: {torun[9]}\t")
                        file.write(f"Baba TC: {torun[10]}\t")
                        file.write(f"Uyruk: {torun[11]}\n")

        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_tc}' OR BABATC = '{baba_tc}') AND TC != '{tc_no}'"
        cursor.execute(query)
        kardesleri_result = cursor.fetchall()

        if kardesleri_result:
            file.write("\nKardeş ve Yeğenleri bilgileri:\n")
            for kardes in kardesleri_result:
                file.write(f"TC: {kardes[1]}\t")
                file.write(f"Adı: {kardes[2]}\t")
                file.write(f"Soyadı: {kardes[3]}\t")
                file.write(f"Doğum Tarihi: {kardes[4]}\t")
                file.write(f"Nufus İli: {kardes[5]}\t")
                file.write(f"Nufus İlçesi: {kardes[6]}\t")
                file.write(f"Anne Adı: {kardes[7]}\t")
                file.write(f"Anne TC: {kardes[8]}\t")
                file.write(f"Baba Adı: {kardes[9]}\t")
                file.write(f"Baba TC: {kardes[10]}\t")
                file.write(f"Uyruk: {kardes[11]}\n")
        
                query = f"SELECT * FROM `101m` WHERE ANNETC = '{kardes[1]}' OR BABATC = '{kardes[1]}'"
                cursor.execute(query)
                yegenleri_result = cursor.fetchall()

            if yegenleri_result:
                file.write("\nYeğen bilgileri:\n")
                for yegen in yegenleri_result:
                    file.write(f"TC: {yegen[1]}\t")
                    file.write(f"Adı: {yegen[2]}\t")
                    file.write(f"Soyadı: {yegen[3]}\t")
                    file.write(f"Doğum Tarihi: {yegen[4]}\t")
                    file.write(f"Nufus İli: {yegen[5]}\t")
                    file.write(f"Nufus İlçesi: {yegen[6]}\t")
                    file.write(f"Anne Adı: {yegen[7]}\t")
                    file.write(f"Anne TC: {yegen[8]}\t")
                    file.write(f"Baba Adı: {yegen[9]}\t")
                    file.write(f"Baba TC: {yegen[10]}\t")
                    file.write(f"Uyruk: {yegen[11]}\n")
                else:
                    file.write("Yeğenlerinin bilgisi bulunamadı.\n")

        else:
            file.write("Kardeş bilgisi bulunamadı.\n")
        
        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_result[8]}' OR BABATC = '{anne_result[10]}') AND TC != '{anne_result[1]}'"
        cursor.execute(query)
        dayı_teyze_result = cursor.fetchall()

        if dayı_teyze_result:
            file.write("\nDayı Teyze ve Kuzenlerinin bilgileri:\n")

            for dayı_teyze in dayı_teyze_result:
                file.write(f"TC: {dayı_teyze[1]}\t")
                file.write(f"Adı: {dayı_teyze[2]}\t")
                file.write(f"Soyadı: {dayı_teyze[3]}\t")
                file.write(f"Doğum Tarihi: {dayı_teyze[4]}\t")
                file.write(f"Nufus İli: {dayı_teyze[5]}\t")
                file.write(f"Nufus İlçesi: {dayı_teyze[6]}\t")
                file.write(f"Anne Adı: {dayı_teyze[7]}\t")
                file.write(f"Anne TC: {dayı_teyze[8]}\t")
                file.write(f"Baba Adı: {dayı_teyze[9]}\t")
                file.write(f"Baba TC: {dayı_teyze[10]}\t")
                file.write(f"Uyruk: {dayı_teyze[11]}\n")

                query = f"SELECT * FROM `101m` WHERE ANNETC = '{dayı_teyze[1]}' OR BABATC = '{dayı_teyze[1]}'"
                cursor.execute(query)
                dayı_teyze_cocuklari_result = cursor.fetchall()

                if dayı_teyze_cocuklari_result:
                    #file.write("\nDayı Teyze Çocukları bilgileri:\n")
                    for atcocuk in dayı_teyze_cocuklari_result:
                        file.write(f"TC: {atcocuk[1]}\t")
                        file.write(f"Adı: {atcocuk[2]}\t")
                        file.write(f"Soyadı: {atcocuk[3]}\t")
                        file.write(f"Doğum Tarihi: {atcocuk[4]}\t")
                        file.write(f"Nufus İli: {atcocuk[5]}\t")
                        file.write(f"Nufus İlçesi: {atcocuk[6]}\t")
                        file.write(f"Anne Adı: {atcocuk[7]}\t")
                        file.write(f"Anne TC: {atcocuk[8]}\t")
                        file.write(f"Baba Adı: {atcocuk[9]}\t")
                        file.write(f"Baba TC: {atcocuk[10]}\t")
                        file.write(f"Uyruk: {atcocuk[11]}\n")
                else:
                    file.write("Dayı Teyze Çocukları bilgisi bulunamadı.\n")
        else:
            file.write("Dayı Teyze bilgisi bulunamadı.\n")

        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{baba_result[8]}' OR BABATC = '{baba_result[10]}') AND TC != '{baba_result[1]}'"
        cursor.execute(query)
        amca_hala_result = cursor.fetchall()

        if amca_hala_result:
            file.write("\nAmca Hala ve Kuzenlerinin bilgileri:\n")
            for amca_hala in amca_hala_result:
                file.write(f"TC: {amca_hala[1]}\t")
                file.write(f"Adı: {amca_hala[2]}\t")
                file.write(f"Soyadı: {amca_hala[3]}\t")
                file.write(f"Doğum Tarihi: {amca_hala[4]}\t")
                file.write(f"Nufus İli: {amca_hala[5]}\t")
                file.write(f"Nufus İlçesi: {amca_hala[6]}\t")
                file.write(f"Anne Adı: {amca_hala[7]}\t")
                file.write(f"Anne TC: {amca_hala[8]}\t")
                file.write(f"Baba Adı: {amca_hala[9]}\t")
                file.write(f"Baba TC: {amca_hala[10]}\t")
                file.write(f"Uyruk: {amca_hala[11]}\n")

                query = f"SELECT * FROM `101m` WHERE ANNETC = '{amca_hala[1]}' OR BABATC = '{amca_hala[1]}'"
                cursor.execute(query)
                amca_hala_cocuklari_result = cursor.fetchall()

                if amca_hala_cocuklari_result:
                    #file.write("\nAmca Hala Çocukları bilgileri:\n")
                    for btcocuk in amca_hala_cocuklari_result:
                        file.write(f"TC: {btcocuk[1]}\t")
                        file.write(f"Adı: {btcocuk[2]}\t")
                        file.write(f"Soyadı: {btcocuk[3]}\t")
                        file.write(f"Doğum Tarihi: {btcocuk[4]}\t")
                        file.write(f"Nufus İli: {btcocuk[5]}\t")
                        file.write(f"Nufus İlçesi: {btcocuk[6]}\t")
                        file.write(f"Anne Adı: {btcocuk[7]}\t")
                        file.write(f"Anne TC: {btcocuk[8]}\t")
                        file.write(f"Baba Adı: {btcocuk[9]}\t")
                        file.write(f"Baba TC: {btcocuk[10]}\t")
                        file.write(f"Uyruk: {btcocuk[11]}\n")
                else:
                    file.write("Amca Hala Çocukları bilgisi bulunamadı.\n")
        else:       
            file.write("Amca Hala bilgisi bulunamadı.\n")
        
else:
    print("Bulunamadı")
cnx.close()
