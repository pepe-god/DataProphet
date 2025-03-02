#!/usr/bin/env python3
import mysql.connector
import csv
import logging
import time
import configparser
import tkinter as tk
from tkinter import messagebox
from contextlib import contextmanager

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG,  # Tüm seviyeleri logla, üretimde INFO veya WARNING'e düşürülebilir
                    format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s')

# Log dosyasına yazdırma (isteğe bağlı, config.ini'den ayarlanabilir)
config = configparser.ConfigParser()
config.read('config.ini')
if config.getboolean('LOGGING', 'log_to_file', fallback=False): # config.ini'de [LOGGING] log_to_file = true ise dosyaya logla
    log_filename = config.get('LOGGING', 'log_filename', fallback='searcher.log') # config.ini'de [LOGGING] log_filename = dosya_adı belirtilebilir
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'))
    logging.getLogger('').addHandler(file_handler) # root logger'a ekle


DB_FIELDS = {
    "TC": "TC", "Adı": "AD", "Soyadı": "SOYAD", "GSM": "GSM", "Baba Adı": "BABAADI", "Baba TC'si": "BABATC",
    "Anne Adı": "ANNEADI", "Anne TC'si": "ANNETC", "Doğum Tarihi": "DOGUMTARIHI", "Ölüm Tarihi": "OLUMTARIHI",
    "Doğum Yeri": "DOGUMYERI", "Memleket İli": "MEMLEKETIL", "Memleket İlçesi": "MEMLEKETILCE",
    "Memleket Köyü": "MEMLEKETKOY", "Adres İli": "ADRESIL", "Adres İlçesi": "ADRESILCE",
    "Aile Sıra No": "AILESIRANO", "Birey Sıra No": "BIREYSIRANO", "Medeni Hal": "MEDENIHAL", "Cinsiyet": "CINSIYET"
}

def validate_tc(tc):
    """TC Kimlik numarasının geçerliliğini kontrol eder."""
    return tc.isdigit() and len(tc) == 11

def build_query(conditions):
    """Verilen koşullara göre SQL sorgusunu oluşturur (parametreleştirilmiş)."""
    query_parts = []
    params = []
    for field, value in conditions.items():
        if value:  # Sadece değeri olan alanlar için koşul ekle
            if field == "DOGUMTARIHI":
                query_parts.append(f"{field} LIKE %s") # Parametre placeholder
                params.append(f"%{value}%") # LIKE için % işaretlerini parametre değerine ekle
            else:
                query_parts.append(f"{field} = %s") # Parametre placeholder
                params.append(value)
    query_condition = " AND ".join(query_parts) if query_parts else "1=1"
    return query_condition, tuple(params) # Sorgu koşulu ve parametreleri tuple olarak döndür

@contextmanager
def db_connection():
    """Veritabanı bağlantısını yönetir (context manager)."""
    conn = None
    try:
        db_config = config['FULLDATA'] # config.ini dosyasından FULLDATA bölümünü al
        conn = mysql.connector.connect(**db_config)
        logging.info("Veritabanına başarıyla bağlanıldı.")
        yield conn
    except mysql.connector.Error as e:
        error_message = f"Veritabanı bağlantı hatası: {e}" # Daha detaylı hata mesajı
        logging.error(error_message, exc_info=True) # exc_info=True ile traceback loga eklenir
        messagebox.showerror("Hata", error_message) # Kullanıcıya da detaylı hata mesajı göster
        yield None  # Hata durumunda None döndür
    finally:
        if conn and conn.is_connected():
            conn.close()
            logging.info("Veritabanı bağlantısı kapatıldı.")


def execute_query(cursor, query, params=None):
    """Verilen sorguyu parametrelerle birlikte çalıştırır ve sonuçları döndürür."""
    try:
        logging.debug(f"Çalıştırılacak sorgu: {query}, Parametreler: {params}") # Parametreleri de logla
        start_time = time.time()
        if params:
            cursor.execute(query, params) # Parametrelerle sorguyu çalıştır
        else:
            cursor.execute(query)
        query_duration = round(time.time() - start_time, 3) # Sorgu süresini hesapla
        logging.debug(f"Sorgu başarıyla çalıştırıldı (Süre: {query_duration}s). Etkilenen satır sayısı: {cursor.rowcount}")
        # Veritabanı performansı için indeksleme önerisi (özellikle WHERE koşulunda kullanılan alanlar için)
        logging.debug("Veritabanı performansını artırmak için sorguda kullanılan alanlar üzerinde indeks oluşturmayı düşünebilirsiniz.")
        # Sorgu optimizasyonu için EXPLAIN kullanımı önerisi
        logging.debug("Sorgu performansını analiz etmek için 'EXPLAIN sorgu' komutunu kullanabilirsiniz.")
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as e:
        error_message = f"Sorgu çalıştırma hatası: {e}" # Daha detaylı hata mesajı
        logging.error(error_message, exc_info=True) # exc_info=True ile traceback loga eklenir
        messagebox.showerror("Hata", error_message) # Kullanıcıya da detaylı hata mesajı göster
        return []


def search(entries):
    """Arama işlemini gerçekleştirir."""
    with db_connection() as db:
        if not db:
            return

        cursor = db.cursor()
        if not cursor:
            logging.error("Cursor oluşturulamadı.")
            return

        # Sadece değeri olan alanları conditions sözlüğüne ekle
        query_conditions_dict = {DB_FIELDS[k]: v.get() for k, v in entries.items() if v.get()} # Daha açıklayıcı değişken adı
        logging.debug(f"Arama koşulları: {query_conditions_dict}")

        if "TC" in query_conditions_dict and not validate_tc(query_conditions_dict["TC"]):
            messagebox.showwarning("Uyarı", "Geçersiz TC Kimlik Numarası")
            logging.warning("Geçersiz TC Kimlik Numarası girildi.")
            return

        query_condition, params = build_query(query_conditions_dict) # Sorgu koşulunu ve parametreleri al
        query = f"SELECT {', '.join(DB_FIELDS.values())} FROM `109m` WHERE {query_condition}"
        logging.info(f"Oluşturulan sorgu: {query}, Parametreler: {params}") # Loga parametreleri de ekle

        start_time = time.time()
        results = execute_query(cursor, query, params) # Parametreleri execute_query'e ilet
        end_time = time.time()
        duration = round(end_time - start_time, 2)

        if not results:
            messagebox.showinfo("Bilgi", "Aramayla eşleşen kayıt bulunamadı.")
            logging.info("Aramayla eşleşen kayıt bulunamadı.")
            return

        filename = f"./index/searcher_{time.strftime('%Y%m%d-%H%M%S')}.csv"
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                csv_writer = csv.writer(f) # Daha açıklayıcı değişken adı
                csv_writer.writerow(DB_FIELDS.keys())
                csv_writer.writerows(results)

                meta = [
                    [],
                    ["Sorgu Koşulları", build_query(query_conditions_dict)[0]], # Sadece sorgu koşulunu meta veriye yaz
                    ["Toplam Süre (s)", duration],
                    ["Toplam Kayıt", len(results)]
                ]
                csv_writer.writerows(meta)

            logging.info(f"Arama sonuçları '{filename}' dosyasına kaydedildi. Toplam kayıt: {len(results)}, Süre: {duration}s")
            messagebox.showinfo("Bilgi", f"'{filename}' oluşturuldu.\nToplam Kayıt: {len(results)}\nSüre: {duration}s")

        except OSError as e:
            file_error_message = f"Dosya yazma hatası: {e}" # Daha detaylı hata mesajı
            logging.error(file_error_message, exc_info=True) # exc_info=True ile traceback loga eklenir
            messagebox.showerror("Hata", file_error_message) # Kullanıcıya da detaylı hata mesajı göster
        finally:
            if cursor:
                cursor.close()
                logging.debug("Cursor kapatıldı.") # Cursor kapatıldığını logla


def create_gui():
    """Grafiksel kullanıcı arayüzünü oluşturur."""
    root = tk.Tk()
    root.title("Searcher")
    entries = {}

    for field in DB_FIELDS:
        frame = tk.Frame(root)
        tk.Label(frame, width=15, text=f"{field}:", anchor='w').pack(side=tk.LEFT)
        entry = tk.Entry(frame)
        entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
        entries[field] = entry
        frame.pack(fill=tk.X, padx=3, pady=3)

    search_button = tk.Button(root, text="Arama Yap", command=lambda: search(entries))
    search_button.pack(pady=20)
    # Birim testleri yazma önerisi (kod kalitesini artırmak için)
    logging.info("Kodun kalitesini ve güvenilirliğini artırmak için birim testleri yazmanız önerilir (unittest veya pytest kullanarak).")

    root.mainloop()


if __name__ == "__main__":
    create_gui()
