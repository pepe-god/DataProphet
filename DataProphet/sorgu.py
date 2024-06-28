import mysql.connector
import csv
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    sorgu = "SELECT * FROM `101m` WHERE TC = %s"
    cursor.execute(sorgu, (tc_no,))
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
            logger.info(f"{ad_soyad} sorgulandı.")

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
            sorgu_kardes = "SELECT * FROM `101m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s"
            cursor.execute(sorgu_kardes, (anne_tc, baba_tc, tc_no))
            kardesler = cursor.fetchall()
            if kardesler:
                writer.writerow(["Kardeş bilgileri"])
                for kardes in kardesler:
                    kisi_bilgisini_csv_yap(writer, kardes)

            # Çocuk bilgileri
            sorgu_cocuklari = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
            cursor.execute(sorgu_cocuklari, (tc_no, tc_no))
            cocuklar = cursor.fetchall()
            if cocuklar:
                writer.writerow(["Çocuk bilgileri"])
                for cocuk in cocuklar:
                    kisi_bilgisini_csv_yap(writer, cocuk)

            # Dayı ve Teyze bilgileri
            sorgu_anne_tc = "SELECT ANNETC, BABATC FROM `101m` WHERE TC = %s"
            cursor.execute(sorgu_anne_tc, (anne_tc,))
            anne_result = cursor.fetchone()
            if anne_result:
                annenin_anne_tc = anne_result[0]
                annenin_baba_tc = anne_result[1]
                sorgu_dayi_teyze = "SELECT * FROM `101m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s"
                cursor.execute(sorgu_dayi_teyze, (annenin_anne_tc, annenin_baba_tc, anne_tc))
                dayi_teyze_sonuclari = cursor.fetchall()
                if dayi_teyze_sonuclari:
                    writer.writerow(["Dayı ve Teyze bilgileri"])
                    for dayi_teyze in dayi_teyze_sonuclari:
                        kisi_bilgisini_csv_yap(writer, dayi_teyze)

            # Amca ve Hala bilgileri
            sorgu_baba_tc = "SELECT ANNETC, BABATC FROM `101m` WHERE TC = %s"
            cursor.execute(sorgu_baba_tc, (baba_tc,))
            baba_result = cursor.fetchone()
            if baba_result:
                babanin_anne_tc = baba_result[0]
                babanin_baba_tc = baba_result[1]
                sorgu_amca_hala = "SELECT * FROM `101m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s"
                cursor.execute(sorgu_amca_hala, (babanin_anne_tc, babanin_baba_tc, baba_tc))
                amca_hala_sonuclari = cursor.fetchall()
                if amca_hala_sonuclari:
                    writer.writerow(["Amca ve Hala bilgileri"])
                    for amca_hala in amca_hala_sonuclari:
                        kisi_bilgisini_csv_yap(writer, amca_hala)
        else:
            logger.info("Kişi bulunamadı.")

try:
    # MySQL bağlantısı oluştur
    cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="101m"
    )
    cursor = cnx.cursor()

    # Aile bilgilerini dosyaya yaz
    write_family_info(cursor, "12345", "sorgu.csv")

except mysql.connector.Error as err:
    logger.error(f"MySQL hatası: {err}")
except Exception as e:
    logger.error(f"Genel hata: {e}")
finally:
    if cnx.is_connected():
        cursor.close()
        cnx.close()
        logger.info("MySQL bağlantısı kapatıldı.")
