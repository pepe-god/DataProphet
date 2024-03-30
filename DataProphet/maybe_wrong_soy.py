from sqlalchemy import create_engine, MetaData, Table, select

def cocuklari_ve_kardesleri_bul(tc, dosya, connection):
    metadata = MetaData(bind=connection)

    # Tabloya erişim için Table objesini oluşturma
    table = Table('101m', metadata, autoload=True)

    query = select([table]).where((table.c.ANNETC == tc) | (table.c.BABATC == tc))
    cocuklar = connection.execute(query).fetchall()

    #dosya.write(f"TC: {tc}\n")
    dosya.write("Çocuklar:\n")
    for cocuk in cocuklar:
        dosya.write(format_kisi_bilgisi(cocuk) + "\n")
        cocuk_tc = cocuk['TC']
        cocuklarin_cocuklarini_bul(cocuk_tc, dosya, connection)  # Çocuğun çocuklarını bulmak için ayrı bir fonksiyon çağrısı

    if not cocuklar:
        #dosya.write("Kişinin çocukları bulunamadı.\n")
        dosya.write("\n")

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
        dosya.write(format_kisi_bilgisi(kardes) + "\n")
        kardes_tc = kardes['TC']
        cocuklarin_cocuklarini_bul(kardes_tc, dosya, connection)  # Kardeşin çocuklarını bulmak için ayrı bir fonksiyon çağrısı

    if not kardesler:
        #dosya.write("Kardeş bulunamadı.\n")
        dosya.write("\n")

    query = select([table]).where(table.c.TC == tc)
    kisi = connection.execute(query).fetchone()

    dosya.write("Kendisi:\n")
    dosya.write(format_kisi_bilgisi(kisi) + "\n")

    if not kisi:
        dosya.write("Kendisi bulunamadı.\n")

    dosya.write("\n")

def cocuklarin_cocuklarini_bul(tc, dosya, connection):
    metadata = MetaData(bind=connection)

    # Tabloya erişim için Table objesini oluşturma
    table = Table('101m', metadata, autoload=True)

    query = select([table]).where((table.c.ANNETC == tc) | (table.c.BABATC == tc))
    cocuklar = connection.execute(query).fetchall()

    #dosya.write(f"TC: {tc}\n")
    dosya.write("Çocukları:\n")
    for cocuk in cocuklar:
        dosya.write(format_kisi_bilgisi(cocuk) + "\n")

    if not cocuklar:
        #dosya.write("Bulunamadı.\n")
        dosya.write("\n")

    dosya.write("\n")

def format_kisi_bilgisi(kisi):
    return ', '.join([f"{key}: {value}" for key, value in kisi._mapping.items()])

def main():
    # Veritabanı bağlantısı oluşturma
    engine = create_engine('mysql+pymysql://root:@localhost/101m')
    connection = engine.connect()

    tc1 = input("TC 1 girin: ")
    tc2 = input("TC 2 girin: ")

    with open("soy.txt", "w") as dosya:
        cocuklari_ve_kardesleri_bul(tc1, dosya, connection)
        cocuklari_ve_kardesleri_bul(tc2, dosya, connection)

    # Bağlantıyı kapatma
    connection.close()

if __name__ == '__main__':
    main()
