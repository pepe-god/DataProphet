import csv
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.database import DatabaseProvider
from core.models import DB_FIELDS_LIST, Person, FAMILY_CSV_HEADER
from core.utils import is_valid_tc, clean_address

class BaseService:
    """Ortak veritabanı işlemlerini içeren temel servis sınıfı."""
    
    def execute_query(self, section: str, query: str, params: tuple = ()) -> List[dict]:
        conn = DatabaseProvider.get_connection(section)
        if not conn:
            return []
            
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            # Kritik olan FULLDATA hatalarını error, diğerlerini warning olarak bas
            level = logging.ERROR if section == 'FULLDATA' else logging.WARNING
            logging.log(level, f"[{section}] Sorgu hatası: {e}\nSorgu: {query}")
            return []
        finally:
            # Bağlantıyı havuza geri bırakmak (close) hayati önem taşır!
            if conn:
                try:
                    conn.close()
                except:
                    pass

    def save_to_csv(self, filename: str, header: List[str], rows: List[List[Any]], metadata: Optional[Dict] = None):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
            if metadata:
                writer.writerow([])
                for k, v in metadata.items():
                    writer.writerow([f"--- {k} ---", v])
        return filename

class SearchService(BaseService):
    def search(self, conditions: Dict[str, str]) -> Tuple[str, int, float]:
        logging.info("--- Gelişmiş Arama Başlatıldı ---")
        clauses, params = [], []
        
        # Kullanılan kriterleri terminale yazdır
        for field, value in conditions.items():
            if not value: continue
            logging.info(f"  [Kriter] {field}: {value}")
            
            if field == "DOGUMTARIHI" and len(value) == 4 and value.isdigit():
                clauses.append("LEFT(DOGUMTARIHI, 4) = %s")
            else:
                clauses.append(f"{field} = %s" if '%' not in value else f"{field} LIKE %s")
            params.append(value)
        
        where = " AND ".join(clauses) if clauses else "1=1"
        query = f"SELECT {', '.join(DB_FIELDS_LIST)} FROM `109m` WHERE {where}"
        
        logging.info("Sorgu veritabanına gönderiliyor...")
        start = time.monotonic()
        results = self.execute_query('FULLDATA', query, tuple(params))
        duration = time.monotonic() - start
        
        logging.info(f"Sorgu tamamlandı. {len(results)} kayıt bulundu. (Süre: {duration:.2f}s)")
        
        # Veri Temizliği (YOK, None vb.)
        rows = []
        for r in results:
            row = []
            for field in DB_FIELDS_LIST:
                val = str(r.get(field, "")).strip()
                if not val or val == "None" or all(word == "YOK" for word in val.split()):
                    row.append("")
                else:
                    row.append(val)
            rows.append(row)
            
        filename = f"./index/search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        logging.info(f"Sonuçlar CSV dosyasına yazılıyor: {filename}")
        self.save_to_csv(filename, DB_FIELDS_LIST, rows, {"Toplam Kayıt": len(rows)})
        
        logging.info("--- Arama İşlemi Bitti ---")
        return filename, len(rows), duration

class FamilyService(BaseService):
    def __init__(self):
        self._person_cache = {} # Önbellek: {tc: Person}

    def get_full_person(self, tc: str) -> Optional[Person]:
        if not is_valid_tc(tc): return None
        
        # 1. Önbellekte var mı kontrol et
        if tc in self._person_cache:
            return self._person_cache[tc]

        res = self.execute_query('FULLDATA', f"SELECT * FROM `109m` WHERE TC = %s", (tc,))
        if not res: return None
        
        p = Person.from_dict(res[0])
        # 2. Adres Bilgisi
        addr_res = self.execute_query('ADRESSDATA', "SELECT GUNCELADRES FROM adresv2 WHERE TC = %s", (tc,))
        p.GUNCELADRES = clean_address(addr_res[0]['GUNCELADRES']) if addr_res else ""
        
        # 3. GSM Bilgisi (GSMDATA veritabanından)
        p.GSM_LIST = self._fetch_gsm_numbers(tc)
        
        # 4. Önbelleğe kaydet
        self._person_cache[tc] = p
        return p

    def _fetch_gsm_numbers(self, tc: str) -> List[str]:
        """GSMDATA veritabanından kişiye ait tüm numaraları çeker."""
        try:
            # Not: Tablo ismi genelde DB ismiyle aynı veya 'gsm' olur
            res = self.execute_query('GSMDATA', "SELECT GSM FROM `140gsm` WHERE TC = %s", (tc,))
            return [str(row['GSM']) for row in res if row['GSM']]
        except Exception as e:
            logging.debug(f"GSM çekme hatası ({tc}): {e}")
            return []

    def get_relatives(self, criteria: str, params: tuple) -> List[Person]:
        res = self.execute_query('FULLDATA', f"SELECT * FROM `109m` WHERE {criteria}", params)
        relatives = []
        for r in res:
            tc = str(r['TC'])
            # Akraba listesi çekerken de önbelleği ve GSM'i kullan
            p = self.get_full_person(tc)
            if p: relatives.append(p)
        return relatives

    def generate_tree(self, main_tc: str) -> str:
        self._person_cache.clear()
        main_p = self.get_full_person(main_tc)
        if not main_p: return "Kayıt bulunamadı."
        
        logging.info(f"!!! Soy ağacı oluşturuluyor: {main_p.AD} {main_p.SOYAD} ({main_tc})")
        
        # Terminal Feedback İyileştirmesi
        if main_p.GSM:
            logging.info(f"    [109M Verisi] GSM: {main_p.GSM}")
        
        if main_p.GSM_LIST:
            # 109M'de olan numarayı listeden çıkarıp sadece 'ek' olanları gösterelim
            extra_gsms = [g for g in main_p.GSM_LIST if g != main_p.GSM]
            if extra_gsms:
                logging.info(f"    [GSMDATA Ek Veri] Numaralar: {', '.join(extra_gsms)}")
            
        results = [("Ana Kayıt", main_p)]
        
        # 1. Üst Soy (Ebeveynler ve Büyük Ebeveynler)
        logging.info(">>> Üst soylar çekiliyor...")
        parents = []
        for tc, label in [(main_p.ANNETC, "Anne"), (main_p.BABATC, "Baba")]:
            if is_valid_tc(tc):
                logging.info(f"[{label}] sorgulanıyor: {tc}")
                p = self.get_full_person(tc)
                if p:
                    results.append((label, p))
                    parents.append((p.TC, label))
                    logging.info(f"--- {label} bulundu: {p.AD} {p.SOYAD}")
                    for r_tc, r_label in [(p.ANNETC, f"Anneanne({label})"), (p.BABATC, f"Dede({label})")]:
                        if is_valid_tc(r_tc):
                            logging.info(f"  [{r_label}] sorgulanıyor: {r_tc}")
                            rp = self.get_full_person(r_tc)
                            if rp: 
                                results.append((r_label, rp))
                                logging.info(f"  --- {r_label} bulundu: {rp.AD} {rp.SOYAD}")

        # 2. Kardeşler ve Yeğenler
        logging.info(">>> Kardeşler ve yeğenler çekiliyor...")
        self._add_siblings(results, main_p)

        # 3. Çocuklar
        logging.info(">>> Çocuklar çekiliyor...")
        self._add_children(results, main_p)

        # 4. Amca/Hala/Dayı/Teyze ve Kuzenler
        logging.info(">>> Geniş aile çekiliyor...")
        for p_tc, p_label in parents:
            logging.info(f"[{p_label}] tarafı geniş aile aranıyor...")
            self._add_extended(results, p_tc, p_label)

        # Kaydetme
        filename = f"./index/{main_p.AD}_{main_p.SOYAD}.csv"
        logging.info(f"Dosya kaydediliyor: {filename}")
        rows = [r[1].to_csv_row(r[0]) for r in results]
        self.save_to_csv(filename, FAMILY_CSV_HEADER, rows)
        logging.info(f"!!! İşlem Tamamlandı. Toplam {len(results)} kayıt yazıldı.")
        return f"Kaydedildi: {filename}"

    def _add_siblings(self, results: list, person: Person):
        clauses, params = [], []
        if is_valid_tc(person.ANNETC): clauses.append("ANNETC = %s"); params.append(person.ANNETC)
        if is_valid_tc(person.BABATC): clauses.append("BABATC = %s"); params.append(person.BABATC)
        if not clauses: return

        criteria = f"({' OR '.join(clauses)}) AND TC != %s"
        params.append(person.TC)
        siblings = self.get_relatives(criteria, tuple(params))
        logging.info(f"Kardeşler listeleniyor ({len(siblings)} kişi bulundu):")
        for s in siblings:
            label = ("Erkek" if s.CINSIYET == "Erkek" else "Kız") + " Kardeş"
            if s.ANNETC != person.ANNETC or s.BABATC != person.BABATC: label += " (Üvey)"
            logging.info(f"  - {label}: {s.AD} {s.SOYAD} ({s.TC})")
            results.append((label, s))
            
            # Yeğenler
            nieces = self.get_relatives("ANNETC = %s OR BABATC = %s", (s.TC, s.TC))
            if nieces:
                logging.info(f"    * {s.AD} kişisinin {len(nieces)} çocuğu (yeğen) bulundu.")
                for n in nieces: results.append(("Yeğen", n))

    def _add_children(self, results: list, person: Person):
        if not is_valid_tc(person.TC): return
        children = self.get_relatives("ANNETC = %s OR BABATC = %s", (person.TC, person.TC))
        if children:
            logging.info(f"Çocuklar listeleniyor ({len(children)} kişi bulundu):")
            for c in children:
                label = "Oğlu" if c.CINSIYET == "Erkek" else "Kızı"
                logging.info(f"  - {label}: {c.AD} {c.SOYAD}")
                results.append((label, c))

    def _add_extended(self, results: list, p_tc: str, p_label: str):
        parent = self.get_full_person(p_tc)
        if not parent: return
        
        clauses, params = [], []
        if is_valid_tc(parent.ANNETC): clauses.append("ANNETC = %s"); params.append(parent.ANNETC)
        if is_valid_tc(parent.BABATC): clauses.append("BABATC = %s"); params.append(parent.BABATC)
        if not clauses: return

        criteria = f"({' OR '.join(clauses)}) AND TC != %s"
        params.append(parent.TC)
        relatives = self.get_relatives(criteria, tuple(params))
        logging.info(f"  {p_label} tarafı kardeşleri ({len(relatives)} kişi bulundu):")
        for r in relatives:
            label = ("Amca" if r.CINSIYET == "Erkek" else "Hala") if p_label == "Baba" else ("Dayı" if r.CINSIYET == "Erkek" else "Teyze")
            logging.info(f"    - {label}: {r.AD} {r.SOYAD} ({r.TC})")
            results.append((label, r))
            # Kuzenler
            cousins = self.get_relatives("ANNETC = %s OR BABATC = %s", (r.TC, r.TC))
            if cousins:
                logging.info(f"      + {r.AD} kişisinin {len(cousins)} çocuğu (kuzen) bulundu.")
                for c in cousins: results.append(("Kuzen", c))
