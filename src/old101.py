#!/usr/bin/env python3
import configparser
import csv
import logging
import os
import time
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector
from mysql.connector import Error

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MSG_WARNING = "Uyarı"
FIELD_SOYADI = "Soyadı"
FIELD_ANNE_ADI = "Anne Adı"
FIELD_BABA_ADI = "Baba Adı"
FIELD_NUFUS_IL = "Nüfus İli"
FIELD_NUFUS_ILCE = "Nüfus İlçesi"
FIELD_DOGUM_YILI = "Doğum Yılı (YYYY)"
FIELD_ANNE_TC = "Anne TC'si"
FIELD_BABA_TC = "Baba TC'si"
CSV_HEADER_TREE = [
    "Kategori",
    "TC",
    "Adı",
    FIELD_SOYADI,
    "Doğum Tarihi",
    "Nufus İli",
    "Nufus İlçesi",
    FIELD_ANNE_ADI,
    "Anne TC",
    FIELD_BABA_ADI,
    "Baba TC",
    "Uyruk",
    "GSM",
]
CSV_HEADER_SEARCH = [
    "TC",
    "Adı",
    FIELD_SOYADI,
    "Doğum Tarihi",
    FIELD_NUFUS_IL,
    FIELD_NUFUS_ILCE,
    FIELD_ANNE_ADI,
    "Anne TC",
    FIELD_BABA_ADI,
    "Baba TC",
    "Uyruk",
]


def read_config():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config.read(config_path)
    if "DATABASE" not in config or "GSMDATA" not in config:
        return None, None
    return config["DATABASE"], config["GSMDATA"]


def validate_tc(tc_no):
    return tc_no and len(tc_no) == 11 and tc_no.isdigit()


def connect_to_database(db_config):
    try:
        cnx = mysql.connector.connect(**db_config)
        logger.info("Veritabanına başarıyla bağlandı.")
        return cnx
    except Error:
        logger.exception("Veritabanı bağlantı hatası")
        return None


def execute_query(cursor, query, params=None, limit=None, offset=None):
    try:
        full_query = query
        full_params = list(params) if params else []
        if limit:
            full_query += " LIMIT %s"
            full_params.append(limit)
        if offset:
            full_query += " OFFSET %s"
            full_params.append(offset)

        start_time = time.time()
        cursor.execute(full_query, tuple(full_params))
        end_time = time.time()

        return True, start_time, end_time, end_time - start_time
    except Error:
        logger.exception("Sorgu çalıştırılırken hata oluştu")
        return False, 0, 0, 0


def build_query(conditions):
    clauses = []
    params = []
    for field, value in conditions.items():
        if not value:
            continue
        if field == "DOGUMTARIHI":
            clauses.append(f"{field} LIKE %s")
            params.append(f"%{value}%")
        else:
            clauses.append(f"{field} = %s")
            params.append(value)
    return " AND ".join(clauses), params


def build_query_display(conditions):
    parts = []
    for field, value in conditions.items():
        if not value:
            continue
        if field == "DOGUMTARIHI":
            parts.append(f"{field} LIKE '%{value}%'")
        else:
            parts.append(f"{field}='{value}'")
    return " AND ".join(parts)


def write_person_info(writer, person, category, gsm_data=None):
    writer.writerow([category] + [str(value) for value in person[1:]] + ([gsm_data] if gsm_data else []))


def get_family_member_by_tc(cursor, tc_no):
    query = "SELECT * FROM `101m` WHERE TC = %s"
    success, _, _, _ = execute_query(cursor, query, (tc_no,))
    if success:
        result = cursor.fetchall()
        return result[0] if result else None
    return None


def get_children_by_parent_tc(cursor, parent_tc):
    query = "SELECT * FROM `101m` WHERE ANNETC = %s OR BABATC = %s"
    success, _, _, _ = execute_query(cursor, query, (parent_tc, parent_tc))
    return cursor.fetchall() if success else []


def get_siblings_by_parent_tc(cursor, anne_tc, baba_tc, tc_no):
    query = "SELECT * FROM `101m` WHERE (ANNETC = %s OR BABATC = %s) AND TC != %s"
    success, _, _, _ = execute_query(cursor, query, (anne_tc, baba_tc, tc_no))
    return cursor.fetchall() if success else []


def get_cousins_by_parent_tc_list(cursor, parent_tc_list):
    if parent_tc_list:
        placeholders = ",".join(["%s"] * len(parent_tc_list))
        query = f"SELECT * FROM `101m` WHERE ANNETC IN ({placeholders}) OR BABATC IN ({placeholders})"
        success, _, _, _ = execute_query(cursor, query, parent_tc_list + parent_tc_list)
        return cursor.fetchall() if success else []
    return []


def get_gsm_data_by_tc(cursor, tc_no):
    query = "SELECT GSM FROM `140gsm` WHERE TC = %s"
    success, _, _, _ = execute_query(cursor, query, (tc_no,))
    if success:
        result = cursor.fetchall()
        return ", ".join([gsm[0] for gsm in result]) if result else "Yok"
    return "Yok"


def _write_person_if_exists(cursor, gsm_cursor, tc, label, writer, prefix):
    person = get_family_member_by_tc(cursor, tc)
    if not person:
        return None
    gsm_data = get_gsm_data_by_tc(gsm_cursor, tc)
    write_person_info(writer, person, prefix + label, gsm_data)
    return person


def _write_ancestors(cursor, gsm_cursor, person, writer, prefix):
    anne_tc = person[8]  # type: ignore[reportArgumentType]
    baba_tc = person[10]  # type: ignore[reportArgumentType]
    anne_result = _write_person_if_exists(cursor, gsm_cursor, anne_tc, "Anne", writer, prefix)
    if anne_result:
        _write_person_if_exists(cursor, gsm_cursor, anne_result[8], "Büyükanne (Anne'nin Anne)", writer, prefix)
        _write_person_if_exists(cursor, gsm_cursor, anne_result[10], "Büyükbaba (Anne'nin Baba)", writer, prefix)
    baba_result = _write_person_if_exists(cursor, gsm_cursor, baba_tc, "Baba", writer, prefix)
    if baba_result:
        _write_person_if_exists(cursor, gsm_cursor, baba_result[8], "Büyükanne (Baba'nın Anne)", writer, prefix)
        _write_person_if_exists(cursor, gsm_cursor, baba_result[10], "Büyükbaba (Baba'nın Baba)", writer, prefix)
    return anne_tc, baba_tc, anne_result, baba_result


def _write_children_and_grandchildren(cursor, gsm_cursor, person, writer, prefix):
    children = get_children_by_parent_tc(cursor, person[1])  # type: ignore[reportArgumentType]
    if not children:
        return 0
    for child in children:
        gsm_data = get_gsm_data_by_tc(gsm_cursor, child[1])
        write_person_info(writer, child, prefix + "Çocuk", gsm_data)
        grandchildren = get_children_by_parent_tc(cursor, child[1])
        for grandchild in grandchildren:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, grandchild[1])
            write_person_info(writer, grandchild, prefix + f"{child[2]} {child[3]}'in Çocuğu", gsm_data)
    return len(children)


def _write_siblings_and_nieces(cursor, gsm_cursor, anne_tc, baba_tc, tc_no, writer, prefix):
    siblings = get_siblings_by_parent_tc(cursor, anne_tc, baba_tc, tc_no)
    niece_count = 0
    if not siblings:
        return 0, 0
    for sibling in siblings:
        gsm_data = get_gsm_data_by_tc(gsm_cursor, sibling[1])
        write_person_info(writer, sibling, prefix + "Kardeşi", gsm_data)
        nieces = get_children_by_parent_tc(cursor, sibling[1])
        niece_count += len(nieces)
        for niece in nieces:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, niece[1])
            write_person_info(writer, niece, prefix + "Yeğeni", gsm_data)
            grandnieces = get_children_by_parent_tc(cursor, niece[1])
            for grandniece in grandnieces:
                gsm_data = get_gsm_data_by_tc(gsm_cursor, grandniece[1])
                write_person_info(writer, grandniece, prefix + f"{niece[2]} {niece[3]}'in Çocuğu", gsm_data)
    return len(siblings), niece_count


def _write_extended_family(cursor, gsm_cursor, parent_result, label, tc_list, writer, prefix):
    if not parent_result:
        return []
    siblings = get_siblings_by_parent_tc(cursor, parent_result[8], parent_result[10], parent_result[1])  # type: ignore[reportArgumentType]
    if not siblings:
        return []
    tc_list.extend([s[1] for s in siblings])
    for sibling in siblings:
        gsm_data = get_gsm_data_by_tc(gsm_cursor, sibling[1])
        write_person_info(writer, sibling, prefix + label, gsm_data)
    return siblings


def _write_cousins(cursor, gsm_cursor, tc_list, writer, prefix):
    cousins = get_cousins_by_parent_tc_list(cursor, tc_list)
    if not cousins:
        return 0, 0
    cousin_child_count = 0
    for cousin in cousins:
        gsm_data = get_gsm_data_by_tc(gsm_cursor, cousin[1])
        write_person_info(writer, cousin, prefix + "Kuzen", gsm_data)
        cousin_children = get_children_by_parent_tc(cursor, cousin[1])
        cousin_child_count += len(cousin_children)
        for child in cousin_children:
            gsm_data = get_gsm_data_by_tc(gsm_cursor, child[1])
            write_person_info(writer, child, prefix + f"{cousin[2]} {cousin[3]}'in Çocuğu", gsm_data)
    return len(cousins), cousin_child_count


def process_family_tree(cursor, gsm_cursor, tc_no, writer, prefix=""):
    main_person = get_family_member_by_tc(cursor, tc_no)
    if not main_person:
        return

    gsm_data = get_gsm_data_by_tc(gsm_cursor, tc_no)
    write_person_info(writer, main_person, prefix + "Ana Kayıt", gsm_data)

    anne_tc, baba_tc, anne_result, baba_result = _write_ancestors(cursor, gsm_cursor, main_person, writer, prefix)
    child_count = _write_children_and_grandchildren(cursor, gsm_cursor, main_person, writer, prefix)
    sibling_count, niece_count = _write_siblings_and_nieces(cursor, gsm_cursor, anne_tc, baba_tc, tc_no, writer, prefix)

    extended_tc_list = []
    dayi_teyze_result = _write_extended_family(
        cursor, gsm_cursor, anne_result, "Dayı/Teyze", extended_tc_list, writer, prefix
    )
    amca_hala_result = _write_extended_family(
        cursor, gsm_cursor, baba_result, "Amca/Hala", extended_tc_list, writer, prefix
    )
    cousin_count, cousin_child_count = _write_cousins(cursor, gsm_cursor, extended_tc_list, writer, prefix)

    return {
        "Kuzen Sayısı": cousin_count,
        "Kardeş Sayısı": sibling_count,
        "Yeğen Sayısı": niece_count,
        "Çocuk Sayısı": child_count,
        "Amca/Hala Sayısı": len(amca_hala_result) if amca_hala_result else 0,
        "Dayı/Teyze Sayısı": len(dayi_teyze_result) if dayi_teyze_result else 0,
        "Kuzen Çocukları Sayısı": cousin_child_count,
    }


def process_tc_number(tc_no):
    if not validate_tc(tc_no):
        messagebox.showwarning(MSG_WARNING, "Geçersiz TC kimlik numarası.")
        return

    db_config, gsm_config = read_config()
    cnx = connect_to_database(db_config)
    if not cnx:
        messagebox.showerror("Hata", "Veritabanına bağlanılamadı.")
        return

    gsm_cnx = connect_to_database(gsm_config)
    if not gsm_cnx:
        messagebox.showerror("Hata", "GSM veritabanına bağlanılamadı.")
        cnx.close()
        return

    try:
        cursor = cnx.cursor()
        gsm_cursor = gsm_cnx.cursor()

        main_person = get_family_member_by_tc(cursor, tc_no)

        if main_person:
            main_person_name = f"{main_person[2]}_{main_person[3]}"  # type: ignore[reportArgumentType]
            os.makedirs("./index", exist_ok=True)
            filename = f"./index/{main_person_name}.csv"

            if os.path.exists(filename) and not messagebox.askyesno(
                "Dosya Var", f"{filename} zaten var. Üzerine yazmak istiyor musunuz?"
            ):
                messagebox.showinfo("İptal", "İşlem iptal edildi.")
                return

            with open(filename, "w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(CSV_HEADER_TREE)
                process_family_tree(cursor, gsm_cursor, tc_no, writer, "")

            messagebox.showinfo("Başarılı", f"Veriler {filename} dosyasına kaydedildi.")
        else:
            messagebox.showinfo("Bulunamadı", "Girilen TC Kimlik Numarası ile eşleşen kayıt bulunamadı.")
    finally:
        cnx.close()
        gsm_cnx.close()


def search_database(entries):
    db_config, _ = read_config()
    db = connect_to_database(db_config)
    if not db:
        messagebox.showerror("Hata", "Veritabanına bağlanılamadı.")
        return

    try:
        cursor = db.cursor()
        query_conditions = {
            field: entries[field].get()
            for field in [
                "TC",
                "Adı",
                FIELD_SOYADI,
                FIELD_DOGUM_YILI,
                FIELD_NUFUS_IL,
                FIELD_NUFUS_ILCE,
                FIELD_ANNE_ADI,
                FIELD_ANNE_TC,
                FIELD_BABA_ADI,
                FIELD_BABA_TC,
                "Uyruk",
            ]
        }

        if query_conditions["TC"] and not validate_tc(query_conditions["TC"]):
            messagebox.showwarning(MSG_WARNING, "Geçersiz TC kimlik numarası.")
            return

        db_fields = {
            "TC": "TC",
            "Adı": "ADI",
            FIELD_SOYADI: "SOYADI",
            FIELD_DOGUM_YILI: "DOGUMTARIHI",
            FIELD_NUFUS_IL: "NUFUSIL",
            FIELD_NUFUS_ILCE: "NUFUSILCE",
            FIELD_ANNE_ADI: "ANNEADI",
            FIELD_ANNE_TC: "ANNETC",
            FIELD_BABA_ADI: "BABAADI",
            FIELD_BABA_TC: "BABATC",
            "Uyruk": "UYRUK",
        }

        query_conditions = {db_fields[field]: value for field, value in query_conditions.items() if value}

        if not query_conditions:
            messagebox.showwarning(MSG_WARNING, "Lütfen en az bir arama kriteri girin.")
            return

        where_clause, where_params = build_query(query_conditions)
        query = "SELECT * FROM `101m` WHERE " + where_clause
        limit, offset, total_records = 5000, 0, 0
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        os.makedirs("./index", exist_ok=True)
        filename = f"./index/searcher_{timestamp}.csv"

        first_query_time = None
        last_query_time = None
        total_duration = 0

        with open(filename, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADER_SEARCH)

            while True:
                success, start_time, end_time, query_time = execute_query(cursor, query, where_params, limit, offset)
                if not success:
                    break

                if first_query_time is None:
                    first_query_time = start_time
                last_query_time = end_time
                total_duration += query_time

                results = cursor.fetchall()
                if not results:
                    break

                for row in results:
                    writer.writerow(list(row[1:]))  # type: ignore[reportArgumentType]
                    total_records += 1

                offset += limit

            writer.writerow([])
            writer.writerow(["Sorgu Koşulları", build_query_display(query_conditions)])
            writer.writerow(
                [
                    "İlk Sorgu Zamanı",
                    time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(first_query_time if first_query_time else time.time())
                    ),
                ]
            )
            writer.writerow(
                [
                    "Son Sorgu Zamanı",
                    time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(last_query_time if last_query_time else time.time())
                    ),
                ]
            )
            writer.writerow(["Toplam Sorgu Süresi (s)", total_duration])
            writer.writerow(["Toplam Kayıt Sayısı", total_records])

        messagebox.showinfo(
            "Bilgi", f"Sonuçlar başarıyla {filename} dosyasına yazıldı. Toplam kayıt sayısı: {total_records}"
        )
    finally:
        db.close()


def main():
    root = tk.Tk()
    root.title("101 Veri Yönetim Sistemi")
    root.geometry("450x550")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    tab_ftr = ttk.Frame(notebook)
    tab_srch = ttk.Frame(notebook)

    notebook.add(tab_ftr, text="Soyağacı Oluşturucu (Family Tree)")
    notebook.add(tab_srch, text="Arama Motoru (Searcher)")

    lbl_ftr = tk.Label(tab_ftr, text="TC Kimlik Numarası:", font=("Arial", 11))
    lbl_ftr.pack(pady=30)

    entry_ftr = tk.Entry(tab_ftr, width=30, font=("Arial", 11))
    entry_ftr.pack(pady=10)

    btn_ftr = tk.Button(
        tab_ftr,
        text="Soyağacı CSV Oluştur",
        font=("Arial", 10),
        bg="#4CAF50",
        fg="white",
        padx=10,
        pady=5,
        command=lambda: process_tc_number(entry_ftr.get()),
    )
    btn_ftr.pack(pady=30)

    fields = [
        "TC",
        "Adı",
        FIELD_SOYADI,
        FIELD_DOGUM_YILI,
        FIELD_NUFUS_IL,
        FIELD_NUFUS_ILCE,
        FIELD_ANNE_ADI,
        FIELD_ANNE_TC,
        FIELD_BABA_ADI,
        FIELD_BABA_TC,
        "Uyruk",
    ]
    entries_srch = {}

    scroll_frame = tk.Frame(tab_srch)
    scroll_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    for field in fields:
        row = tk.Frame(scroll_frame)
        tk.Label(row, width=18, text=field + ": ", anchor="w", font=("Arial", 9)).pack(side=tk.LEFT, pady=2)
        ent = tk.Entry(row, font=("Arial", 9))
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X, pady=2)
        row.pack(side=tk.TOP, fill=tk.X)
        entries_srch[field] = ent

    btn_srch = tk.Button(
        tab_srch,
        text="Detaylı Arama Yap",
        font=("Arial", 10),
        bg="#2196F3",
        fg="white",
        padx=10,
        pady=5,
        command=lambda: search_database(entries_srch),
    )
    btn_srch.pack(side=tk.BOTTOM, pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
