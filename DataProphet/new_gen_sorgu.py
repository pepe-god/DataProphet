import mysql.connector
import csv

def kisi_bilgisini_csv_yap(writer, kisi):
    writer.writerow([
        kisi[1],  # TC
        kisi[2],  # Adı
        kisi[3],  # Soyadı
        kisi[4],  # Doğum Tarihi
        kisi[5],  # Nufus İli
        kisi[6],  # Nufus İlçesi
        kisi[7],  # Anne Adı
        kisi[8],  # Anne TC
        kisi[9],  # Baba Adı
        kisi[10], # Baba TC
        kisi[11]  # Uyruk
    ])

def kisi_bilgisini_al(cursor, tc_no):
    sorgu = f"SELECT * FROM `101m` WHERE TC = '{tc_no}'"
    cursor.execute(sorgu)
    return cursor.fetchone()

def write_family_info(cursor, tc_no, output_file):
    with open(output_file, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["TC", "Adı", "Soyadı", "Doğum Tarihi", "Nufus İli", "Nufus İlçesi", "Anne Adı", "Anne TC", "Baba Adı", "Baba TC", "Uyruk"])

        kisi = kisi_bilgisini_al(cursor, tc_no)
        if kisi:
            writer.writerow(["Bulunan kayıt"])
            kisi_bilgisini_csv_yap(writer, kisi)
            ad_soyad = kisi[2] + " " + kisi[3]
            print(f"{ad_soyad} sorgulandı.")

            # Anne bilgileri
            anne_tc = kisi[8]
            anne = kisi_bilgisini_al(cursor, anne_tc)
            if anne:
                writer.writerow(["Anne bilgileri"])
                kisi_bilgisini_csv_yap(writer, anne)

            # Baba bilgileri
            baba_tc = kisi[10]
            baba = kisi_bilgisini_al(cursor, baba_tc)
            if baba:
                writer.writerow(["Baba bilgileri"])
                kisi_bilgisini_csv_yap(writer, baba)

            # Kardeş bilgileri
            sorgu_kardes = f"SELECT * FROM `101m` WHERE (ANNETC = '{anne_tc}' OR BABATC = '{baba_tc}') AND TC != '{tc_no}'"
            cursor.execute(sorgu_kardes)
            kardesler = cursor.fetchall()
            if kardesler:
                writer.writerow(["Kardeş bilgileri"])
                for kardes in kardesler:
                    kisi_bilgisini_csv_yap(writer, kardes)

            # Çocuk bilgileri
            sorgu_cocuklari = f"SELECT * FROM `101m` WHERE ANNETC = '{tc_no}' OR BABATC = '{tc_no}'"
            cursor.execute(sorgu_cocuklari)
            cocuklar = cursor.fetchall()
            if cocuklar:
                writer.writerow(["Çocuk bilgileri"])
                for cocuk in cocuklar:
                    kisi_bilgisini_csv_yap(writer, cocuk)

            # Dayı ve Teyze bilgileri
            sorgu_anne_tc = f"SELECT ANNETC, BABATC FROM `101m` WHERE TC = '{anne_tc}'"
            cursor.execute(sorgu_anne_tc)
            anne_result = cursor.fetchone()
            if anne_result:
                annenin_anne_tc = anne_result[0]
                annenin_baba_tc = anne_result[1]
                sorgu_dayi_teyze = f"SELECT * FROM `101m` WHERE (ANNETC = '{annenin_anne_tc}' OR BABATC = '{annenin_baba_tc}') AND TC != '{anne_tc}'"
                cursor.execute(sorgu_dayi_teyze)
                dayi_teyze_sonuclari = cursor.fetchall()
                if dayi_teyze_sonuclari:
                    writer.writerow(["Dayı ve Teyze bilgileri"])
                    for dayi_teyze in dayi_teyze_sonuclari:
                        kisi_bilgisini_csv_yap(writer, dayi_teyze)

            # Amca ve Hala bilgileri
            sorgu_baba_tc = f"SELECT ANNETC, BABATC FROM `101m` WHERE TC = '{baba_tc}'"
            cursor.execute(sorgu_baba_tc)
            baba_result = cursor.fetchone()
            if baba_result:
                babanin_anne_tc = baba_result[0]
                babanin_baba_tc = baba_result[1]
                sorgu_amca_hala = f"SELECT * FROM `101m` WHERE (ANNETC = '{babanin_anne_tc}' OR BABATC = '{babanin_baba_tc}') AND TC != '{baba_tc}'"
                cursor.execute(sorgu_amca_hala)
                amca_hala_sonuclari = cursor.fetchall()
                if amca_hala_sonuclari:
                    writer.writerow(["Amca ve Hala bilgileri"])
                    for amca_hala in amca_hala_sonuclari:
                        kisi_bilgisini_csv_yap(writer, amca_hala)
        else:
            print("Kişi bulunamadı.")

# MySQL bağlantısı oluştur
cnx = mysql.connector.connect(host="localhost", user="root", password="", database="101m")
cursor = cnx.cursor()

# Aile bilgilerini dosyaya yaz
write_family_info(cursor, "11223344", "sorgu.csv")

# Bağlantıyı kapat
cnx.close()
