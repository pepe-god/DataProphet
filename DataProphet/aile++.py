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
    with open("aile++.txt", "w", encoding="utf-8") as file:
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
        cocuklari = cursor.fetchall()

        if cocuklari:
            file.write("\nÇocuklarının bilgileri:\n")
            for k in cocuklari:
                file.write(f"{k}\n")
        else:
            file.write("Çocuklarının bilgileri bulunamadı.\n")

        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_tc}' OR BABATC = '{baba_tc}') AND TC != '{tc_no}'"
        cursor.execute(query)
        kardes = cursor.fetchall()

        if kardes:
            file.write("\nKardeş bilgileri:\n")
            for k in kardes:
                file.write(f"{k}\n")
        else:
            file.write("Kardeş bilgisi bulunamadı.\n")

        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_result[8]}' OR BABATC = '{anne_result[10]}') AND TC != '{anne_result[1]}'"
        cursor.execute(query)
        dayı_teyze = cursor.fetchall()

        if dayı_teyze:
            file.write("\nDayı Teyze bilgileri:\n")
            for k in dayı_teyze:
                file.write(f"{k}\n")
        else:
            file.write("Dayı Teyze bilgisi bulunamadı.\n")

        query = f"SELECT * FROM `101m` WHERE (ANNETC = '{baba_result[8]}' OR BABATC = '{baba_result[10]}') AND TC != '{baba_result[1]}'"
        cursor.execute(query)
        amca_hala = cursor.fetchall()

        if amca_hala:
            file.write("\nAmca Hala bilgileri:\n")
            for k in amca_hala:
                file.write(f"{k}\n")
        else:       
            file.write("Amca Hala bilgisi bulunamadı.\n")
else:
    print("Bulunamadı")
cnx.close()
