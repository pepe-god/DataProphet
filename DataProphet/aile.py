from sqlalchemy import create_engine, MetaData, Table, select

def cocuklari_ve_kardesleri_bul(tc, dosya, connection):
    metadata = MetaData(bind=connection)

    # Tabloya erişim için Table objesini oluşturma
    table = Table('101m', metadata, autoload=True)

    query = select([table]).where((table.c.ANNETC == tc) | (table.c.BABATC == tc))
    cocuklar = connection.execute(query).fetchall()

    dosya.write(f"TC: {tc}\n")
    dosya.write("Çocuklar:\n")
    for cocuk in cocuklar:
        dosya.write(str(cocuk) + "\n")

    if not cocuklar:
        dosya.write("Kişinin çocukları bulunamadı.\n")

    query = select([table.c.ANNETC, table.c.BABATC]).where(table.c.TC == tc)
    parametreler = connection.execute(query).fetchone()
    if not parametreler:
        dosya.write("Bu TC numarasına ait kişi bulunamadı.\n")
        return

    anne_tc, baba_tc = parametreler

    query = select([table]).where(((table.c.ANNETC == anne_tc) | (table.c.BABATC == baba_tc)) & (table.c.TC != tc))
    kardesler = connection.execute(query).fetchall()

    dosya.write("Kardeşler:\n")
    for kardes in kardesler:
        dosya.write(str(kardes) + "\n")

    if not kardesler:
        dosya.write("Kardeş bulunamadı.\n")

    query = select([table]).where(table.c.TC == anne_tc)
    anne = connection.execute(query).fetchone()

    dosya.write("Anne Bilgileri:\n")
    dosya.write(str(anne) + "\n")

    if not anne:
        dosya.write("Anne bilgileri bulunamadı.\n")

    query = select([table]).where(table.c.TC == baba_tc)
    baba = connection.execute(query).fetchone()

    dosya.write("Baba Bilgileri:\n")
    dosya.write(str(baba) + "\n")

    if not baba:
        dosya.write("Baba bilgileri bulunamadı.\n")

    query = select([table]).where(table.c.TC == tc)
    kisi = connection.execute(query).fetchone()

    dosya.write("Kişi Bilgileri:\n")
    dosya.write(str(kisi) + "\n")

    if not kisi:
        dosya.write("Kişi bilgileri bulunamadı.\n")

    dosya.write("\n")

def main():
    # Veritabanı bağlantısı oluşturma
    engine = create_engine('mysql+pymysql://root:@localhost/101m')
    connection = engine.connect()

    tc1 = input("TC 1 girin: ")
    tc2 = input("TC 2 girin: ")

    with open("aile.txt", "w") as dosya:
        cocuklari_ve_kardesleri_bul(tc1, dosya, connection)
        cocuklari_ve_kardesleri_bul(tc2, dosya, connection)

    # Bağlantıyı kapatma
    connection.close()

if __name__ == "__main__":
    main()