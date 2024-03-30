import mysql.connector

def write_person_info(file, person):
    file.write(f"TC: {person[1]}\tAdı: {person[2]}\tSoyadı: {person[3]}\tDoğum Tarihi: {person[4]}\tNufus İli: {person[5]}\tNufus İlçesi: {person[6]}\tAnne Adı: {person[7]}\tAnne TC: {person[8]}\tBaba Adı: {person[9]}\tBaba TC: {person[10]}\tUyruk: {person[11]}\n")

def get_person(cursor, tc_no):
    query = f"SELECT * FROM `101m` WHERE TC = '{tc_no}'"
    cursor.execute(query)
    return cursor.fetchone()

def get_siblings(cursor, parent_tc, relation_type):
    query = f"SELECT * FROM `101m` WHERE {relation_type} = '{parent_tc}'"
    cursor.execute(query)
    return cursor.fetchall()

def write_family_info(cursor, tc_no, output_file):
    person = get_person(cursor, tc_no)
    if person:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write("Bulunan kayıt:\n")
            write_person_info(file, person)

            # Anne bilgileri
            mother = get_person(cursor, person[8])
            if mother:
                file.write("\nAnne bilgileri:\n")
                write_person_info(file, mother)

                # Anne tarafından kardeşler
                siblings = get_siblings(cursor, person[8], "ANNETC")
                if siblings:
                    file.write("\nAnne Tarafından Kardeş bilgileri:\n")
                    for sibling in siblings:
                        write_person_info(file, sibling)

            # Baba bilgileri
            father = get_person(cursor, person[10])
            if father:
                file.write("\nBaba bilgileri:\n")
                write_person_info(file, father)

                # Baba tarafından kardeşler
                siblings = get_siblings(cursor, person[10], "BABATC")
                if siblings:
                    file.write("\nBaba Tarafından Kardeş bilgileri:\n")
                    for sibling in siblings:
                        write_person_info(file, sibling)

    else:
        print("Bulunamadı")

# MySQL bağlantısı oluştur
cnx = mysql.connector.connect(host="localhost", user="root", password="", database="101m")
cursor = cnx.cursor()

# Aile bilgilerini yazdır
write_family_info(cursor, "12345678912", "kisi_bilgileri.txt")

# Bağlantıyı kapat
cnx.close()
