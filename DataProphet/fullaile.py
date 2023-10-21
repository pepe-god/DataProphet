import mysql.connector

# MySQL bağlantısı oluşturma
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="101m"
)

# Veritabanı işlemleri için cursor oluşturma
cursor = db.cursor()

def cocuklari_ve_kardesleri_bul(tc, dosya):
    dosya.write(f"TC: {tc}\n")

    # Kişinin çocuklarını bul
    query_cocuklar = f"SELECT * FROM `101m` WHERE ANNETC='{tc}' OR BABATC='{tc}';"
    cursor.execute(query_cocuklar)
    cocuklar = cursor.fetchall()

    dosya.write("Çocuklar:\n")
    for cocuk in cocuklar:
        dosya.write(str(cocuk) + "\n")

    if not cocuklar:
        dosya.write("Kişinin çocukları bulunamadı.\n")

    # Kişinin ANNETC ve BABATC değerlerini al
    query_parametreler = f"SELECT ANNETC, BABATC FROM `101m` WHERE TC='{tc}';"
    cursor.execute(query_parametreler)
    parametreler = cursor.fetchone()
    if not parametreler:
        dosya.write("Bu TC numarasına ait kişi bulunamadı.\n")
        return

    anne_tc, baba_tc = parametreler

    # Kişinin kardeşlerini bulma
    query_kardesler = f"SELECT * FROM `101m` WHERE (ANNETC='{anne_tc}' OR BABATC='{baba_tc}') AND TC != '{tc}';"
    cursor.execute(query_kardesler)
    kardesler = cursor.fetchall()

    dosya.write("Kardeşler:\n")
    for kardes in kardesler:
        dosya.write(str(kardes) + "\n")

    if not kardesler:
        dosya.write("Kardeş bulunamadı.\n")

    # Kişinin anne bilgilerini bulma
    query_anne = f"SELECT * FROM `101m` WHERE TC='{anne_tc}';"
    cursor.execute(query_anne)
    anne = cursor.fetchone()

    dosya.write("Anne Bilgileri:\n")
    dosya.write(str(anne) + "\n")

    if not anne:
        dosya.write("Anne bilgileri bulunamadı.\n")

    # Kişinin baba bilgilerini bulma
    query_baba = f"SELECT * FROM `101m` WHERE TC='{baba_tc}';"
    cursor.execute(query_baba)
    baba = cursor.fetchone()

    dosya.write("Baba Bilgileri:\n")
    dosya.write(str(baba) + "\n")

    if not baba:
        dosya.write("Baba bilgileri bulunamadı.\n")

    # Kişinin kendi bilgilerini bulma
    query_kisi = f"SELECT * FROM `101m` WHERE TC='{tc}';"
    cursor.execute(query_kisi)
    kisi = cursor.fetchone()

    dosya.write("Kişi Bilgileri:\n")
    dosya.write(str(kisi) + "\n")

    if not kisi:
        dosya.write("Kişi bilgileri bulunamadı.\n")

    dosya.write("\n")

def main():
    tc1 = input("TC 1 girin: ")
    tc2 = input("TC 2 girin: ")

    with open("aile_bilgileri.txt", "w") as dosya:
        cocuklari_ve_kardesleri_bul(tc1, dosya)
        cocuklari_ve_kardesleri_bul(tc2, dosya)

    # Bağlantıyı kapatma
    cursor.close()
    db.close()

if __name__ == "__main__":
    main()
