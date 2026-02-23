from dataclasses import dataclass, fields
from typing import Any, Dict, List

# Veritabanı sütun isimleri
DB_FIELDS_LIST = [
    "TC", "AD", "SOYAD", "GSM", "BABAADI", "BABATC", "ANNEADI", "ANNETC",
    "DOGUMTARIHI", "OLUMTARIHI", "DOGUMYERI", "MEMLEKETIL", "MEMLEKETILCE",
    "MEMLEKETKOY", "ADRESIL", "ADRESILCE", "AILESIRANO", "BIREYSIRANO",
    "MEDENIHAL", "CINSIYET"
]

# GUI için eşleştirme
SEARCH_FIELDS_MAP = {
    "TC": "TC", "Adı": "AD", "Soyadı": "SOYAD", "GSM": "GSM",
    "Baba Adı": "BABAADI", "Baba TC'si": "BABATC",
    "Anne Adı": "ANNEADI", "Anne TC'si": "ANNETC",
    "Doğum Tarihi": "DOGUMTARIHI", "Ölüm Tarihi": "OLUMTARIHI",
    "Doğum Yeri": "DOGUMYERI", "Memleket İli": "MEMLEKETIL",
    "Memleket İlçesi": "MEMLEKETILCE", "Memleket Köyü": "MEMLEKETKOY",
    "Adres İli": "ADRESIL", "Adres İlçesi": "ADRESILCE",
    "Aile Sıra No": "AILESIRANO", "Birey Sıra No": "BIREYSIRANO",
    "Medeni Hal": "MEDENIHAL", "Cinsiyet": "CINSIYET"
}

# Soy Ağacı Çıktısı İçin Başlıklar
FAMILY_CSV_HEADER = [
    "Kategori", "TC", "AD", "SOYAD", "GSM", "DOGUMTARIHI", "OLUMTARIHI",
    "DOGUMYERI", "MEMLEKETIL", "MEMLEKETILCE", "MEMLEKETKOY", "ADRESIL",
    "ADRESILCE", "GUNCELADRES", "MEDENIHAL", "CINSIYET"
]

@dataclass
class Person:
    TC: str = ""
    AD: str = ""
    SOYAD: str = ""
    GSM: str = "" # Ana veritabanındaki GSM
    GSM_LIST: List[str] = None # GSMDATA'dan gelecek çoklu numaralar
    BABAADI: str = ""
    BABATC: str = ""
    ANNEADI: str = ""
    ANNETC: str = ""
    DOGUMTARIHI: str = ""
    OLUMTARIHI: str = ""
    DOGUMYERI: str = ""
    MEMLEKETIL: str = ""
    MEMLEKETILCE: str = ""
    MEMLEKETKOY: str = ""
    ADRESIL: str = ""
    ADRESILCE: str = ""
    AILESIRANO: str = ""
    BIREYSIRANO: str = ""
    MEDENIHAL: str = ""
    CINSIYET: str = ""
    GUNCELADRES: str = ""

    def __post_init__(self):
        if self.GSM_LIST is None:
            self.GSM_LIST = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)

    def to_csv_row(self, category: str = "Veri") -> List[str]:
        # Çoklu GSM numaralarını birleştir
        all_gsms = [self.GSM] if self.GSM else []
        if self.GSM_LIST:
            all_gsms.extend([g for g in self.GSM_LIST if g != self.GSM])
        gsm_str = " | ".join(all_gsms)

        # Ham veri listesi
        row = [
            category, self.TC, self.AD, self.SOYAD, gsm_str,
            self.DOGUMTARIHI, self.OLUMTARIHI, self.DOGUMYERI,
            self.MEMLEKETIL, self.MEMLEKETILCE, self.MEMLEKETKOY,
            self.ADRESIL, self.ADRESILCE, self.GUNCELADRES,
            self.MEDENIHAL, self.CINSIYET
        ]
        
        # Temizleme Mantığı: "YOK", "YOK YOK", "None" vb. durumları boşaltır
        cleaned_row = []
        for val in row:
            s_val = str(val).strip()
            # Eğer değer boşsa, "None" ise veya sadece "YOK" kelimelerinden oluşuyorsa
            if not s_val or s_val == "None" or all(word == "YOK" for word in s_val.split()):
                cleaned_row.append("")
            else:
                cleaned_row.append(s_val)
                
        return cleaned_row
