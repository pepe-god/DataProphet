import pytest

DEFAULT_CITY = "İSTANBUL"


@pytest.fixture
def sample_person_dict():
    """Test için örnek Person sözlüğü."""
    return {
        "TC": "12345678901",
        "AD": "AHMET",
        "SOYAD": "YILMAZ",
        "GSM": "5321234567",
        "BABAADI": "MEHMET",
        "BABATC": "11111111111",
        "ANNEADI": "AYŞE",
        "ANNETC": "22222222222",
        "DOGUMTARIHI": "01/01/1990",
        "OLUMTARIHI": "",
        "DOGUMYERI": DEFAULT_CITY,
        "MEMLEKETIL": DEFAULT_CITY,
        "MEMLEKETILCE": "KADIKÖY",
        "MEMLEKETKOY": "",
        "ADRESIL": DEFAULT_CITY,
        "ADRESILCE": "KADIKÖY",
        "AILESIRANO": "1",
        "BIREYSIRANO": "1",
        "MEDENIHAL": "Evli",
        "CINSIYET": "Erkek",
    }


@pytest.fixture
def tmp_index_dir(tmp_path):
    """Test için geçici index dizini."""
    index_dir = tmp_path / "index"
    index_dir.mkdir()
    return index_dir
