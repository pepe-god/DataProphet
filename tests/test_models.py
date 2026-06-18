from src.models import DB_FIELDS_LIST, FAMILY_CSV_HEADER, SEARCH_FIELDS_MAP, Person


class TestPersonFromDict:
    def test_full_dict(self, sample_person_dict):
        p = Person.from_dict(sample_person_dict)
        assert p.TC == "12345678901"
        assert p.AD == "AHMET"
        assert p.SOYAD == "YILMAZ"
        assert p.GSM == "5321234567"
        assert p.CINSIYET == "Erkek"

    def test_missing_fields(self):
        p = Person.from_dict({"TC": "11111111111", "AD": "Ali"})
        assert p.TC == "11111111111"
        assert p.AD == "Ali"
        assert p.SOYAD == ""
        assert p.GSM_LIST == []

    def test_extra_fields_ignored(self):
        data = {"TC": "11111111111", "AD": "Ali", "UNKNOWN_FIELD": "test"}
        p = Person.from_dict(data)
        assert p.TC == "11111111111"
        assert not hasattr(p, "UNKNOWN_FIELD")

    def test_empty_dict(self):
        p = Person.from_dict({})
        assert p.TC == ""
        assert p.GSM_LIST == []


class TestPersonToCsvRow:
    def test_basic_row(self, sample_person_dict):
        p = Person.from_dict(sample_person_dict)
        row = p.to_csv_row("Ana Kayıt")
        assert row[0] == "Ana Kayıt"
        assert row[1] == "12345678901"
        assert row[2] == "AHMET"
        assert row[3] == "YILMAZ"

    def test_yok_values_cleaned(self):
        p = Person.from_dict({"TC": "111", "AD": "YOK", "SOYAD": "YOK YOK", "GSM": "None"})
        row = p.to_csv_row()
        assert row[2] == ""
        assert row[3] == ""
        assert row[4] == ""

    def test_empty_values_cleaned(self):
        p = Person.from_dict({"TC": "111", "AD": "", "SOYAD": ""})
        row = p.to_csv_row()
        assert row[2] == ""
        assert row[3] == ""

    def test_gsm_list_included(self):
        p = Person.from_dict({"TC": "111", "GSM": "5321112233"})
        p.GSM_LIST = ["5321112233", "5339998877"]
        row = p.to_csv_row()
        assert "5321112233" in row[4]
        assert "5339998877" in row[4]

    def test_gsm_list_no_duplicates(self):
        p = Person.from_dict({"TC": "111", "GSM": "5321112233"})
        p.GSM_LIST = ["5321112233"]
        row = p.to_csv_row()
        assert row[4] == "5321112233"


class TestModelsConstants:
    def test_db_fields_count(self):
        assert len(DB_FIELDS_LIST) == 20

    def test_search_fields_count(self):
        assert len(SEARCH_FIELDS_MAP) == 20

    def test_family_csv_header_count(self):
        assert len(FAMILY_CSV_HEADER) == 16

    def test_search_fields_map_values_match_db_fields(self):
        for db_field in SEARCH_FIELDS_MAP.values():
            assert db_field in DB_FIELDS_LIST
