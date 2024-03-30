import mysql.connector

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="101m"
)

cursor = cnx.cursor()

tc_no = "12345678901"  # kişi tc si buraya
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

        query = f"SELECT * FROM `101m` WHERE ANNETC = '{anne_tc}' AND TC != '{tc_no}'"
        cursor.execute(query)
        anneden_kardes_result = cursor.fetchall()

        if anneden_kardes_result:
            file.write("\nAnne Tarafından Kardeş bilgileri:\n")
            for kardes in anneden_kardes_result:
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
        else:
            file.write("\nAnne Tarafından Kardeş bilgisi bulunamadı.\n")

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

        query = f"SELECT * FROM `101m` WHERE BABATC = '{baba_tc}' AND TC != '{tc_no}'"
        cursor.execute(query)
        babadan_kardes_result = cursor.fetchall()

        if babadan_kardes_result:
            file.write("\nBaba Tarafından Kardeş bilgileri:\n")
            for kardes in babadan_kardes_result:
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
        else:
            file.write("\nBaba Tarafından Kardeş bilgisi bulunamadı.\n")

else:
    print("Bulunamadı")
cnx.close()
