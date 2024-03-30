import mysql.connector

# Kişi bilgisini dosyaya yazma fonksiyonu
def kisi_bilgisini_yaz(file, kisi):
    file.write(f"TC: {kisi[1]}\tAdı: {kisi[2]}\tSoyadı: {kisi[3]}\tDoğum Tarihi: {kisi[4]}\tNufus İli: {kisi[5]}\tNufus İlçesi: {kisi[6]}\tAnne Adı: {kisi[7]}\tAnne TC: {kisi[8]}\tBaba Adı: {kisi[9]}\tBaba TC: {kisi[10]}\tUyruk: {kisi[11]}\n")

# Kişi bilgisini veritabanından alma fonksiyonu
def kisi_bilgisini_al(cursor, tc_no):
    sorgu = f"SELECT * FROM `101m` WHERE TC = '{tc_no}'"
    cursor.execute(sorgu)
    return cursor.fetchone()

# Aile bilgilerini dosyaya yazma fonksiyonu
def write_family_info(cursor, tc_no, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        kisi = kisi_bilgisini_al(cursor, tc_no)
        if kisi:
            file.write("Bulunan kayıt:\n")
            kisi_bilgisini_yaz(file, kisi)

            # Anne bilgileri
            anne_tc = kisi[8]
            sorgu_anne = f"SELECT * FROM `101m` WHERE TC = '{anne_tc}'"
            cursor.execute(sorgu_anne)
            anne = cursor.fetchone()
            if anne:
                file.write("\nAnne bilgileri:\n")
                kisi_bilgisini_yaz(file, anne)

            # Baba bilgileri
            baba_tc = kisi[10]
            sorgu_baba = f"SELECT * FROM `101m` WHERE TC = '{baba_tc}'"
            cursor.execute(sorgu_baba)
            baba = cursor.fetchone()
            if baba:
                file.write("\nBaba bilgileri:\n")
                kisi_bilgisini_yaz(file, baba)

            # Kardeş bilgileri
            sorgu_kardes = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_tc}' OR BABATC = '{baba_tc}') AND TC != '{tc_no}'"
            cursor.execute(sorgu_kardes)
            kardesler = cursor.fetchall()
            if kardesler:
                file.write("\nKardeş bilgileri:\n")
                for kardes in kardesler:
                    kisi_bilgisini_yaz(file, kardes)

            # Çocuk bilgileri
            sorgu_cocuklari = f"SELECT * FROM `101m` WHERE ANNETC = '{tc_no}' OR BABATC = '{tc_no}'"
            cursor.execute(sorgu_cocuklari)
            cocuklar = cursor.fetchall()
            if cocuklar:
                file.write("\nÇocuk bilgileri:\n")
                for cocuk in cocuklar:
                    kisi_bilgisini_yaz(file, cocuk)

            # Dayı ve Teyze bilgileri
            sorgu_anne_tc = f"SELECT ANNETC, BABATC FROM `101m` WHERE TC = '{anne_tc}'"
            cursor.execute(sorgu_anne_tc)
            anne_result = cursor.fetchone()
            if anne_result:
                annenin_anne_tc = anne_result[0]  # Anne kişisinin ANNETC değeri
                annenin_baba_tc = anne_result[1]  # Anne kişisinin BABATC değeri
                annenin_kendi_tc = anne_result[1]
                sorgu_dayi_teyze = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_result[0]}' OR BABATC = '{anne_result[1]}') AND TC != '{annenin_kendi_tc}'"
                cursor.execute(sorgu_dayi_teyze)
                dayi_teyze_sonuclari = cursor.fetchall()
                if dayi_teyze_sonuclari:
                    file.write("\nDayı ve Teyze bilgileri:\n")
                    for dayi_teyze in dayi_teyze_sonuclari:
                        kisi_bilgisini_yaz(file, dayi_teyze)

            # Amca ve Hala bilgileri
            sorgu_baba_tc = f"SELECT ANNETC, BABATC FROM `101m` WHERE TC = '{baba_tc}'"
            cursor.execute(sorgu_baba_tc)
            baba_result = cursor.fetchone()
            if baba_result:
                babanin_anne_tc = baba_result[0]  # Baba kişisinin ANNETC değeri
                babanin_baba_tc = baba_result[1]  # Baba kişisinin BABATC değeri
                babanin_kendi_tc = baba_result[1]
                sorgu_amca_hala = f"SELECT * FROM `101m` WHERE (ANNETC = '{baba_result[0]}' OR BABATC = '{baba_result[1]}') AND TC != '{babanin_kendi_tc}'"
                cursor.execute(sorgu_amca_hala)
                amca_hala_sonuclari = cursor.fetchall()
                if amca_hala_sonuclari:
                    file.write("\nDayı ve Teyze bilgileri:\n")
                    for amca_hala in amca_hala_sonuclari:
                        kisi_bilgisini_yaz(file, amca_hala)
        else:
             print("Kişi bulunamadı.")

# MySQL bağlantısı oluştur
cnx = mysql.connector.connect(host="localhost", user="root", password="", database="101m")
cursor = cnx.cursor()

# Aile bilgilerini dosyaya yaz
write_family_info(cursor, "11223344", "aile.txt")

# Bağlantıyı kapat
cnx.close()
