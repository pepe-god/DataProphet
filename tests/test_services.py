import os
from unittest.mock import patch

from src.services import BaseService, FamilyService, SearchService


class TestBaseService:
    def test_save_to_csv(self, tmp_path):
        service = BaseService()
        filename = str(tmp_path / "test.csv")
        header = ["Col1", "Col2"]
        rows = [["A", "B"], ["C", "D"]]
        result = service.save_to_csv(filename, header, rows)
        assert os.path.exists(result)
        with open(result, encoding="utf-8") as f:
            lines = f.readlines()
        assert "Col1,Col2\n" in lines[0]

    def test_save_to_csv_with_metadata(self, tmp_path):
        service = BaseService()
        filename = str(tmp_path / "test_meta.csv")
        header = ["Col1"]
        rows = [["A"]]
        metadata = {"Toplam": 1}
        service.save_to_csv(filename, header, rows, metadata)
        with open(filename, encoding="utf-8") as f:
            content = f.read()
        assert "Toplam" in content

    @patch("src.services.DatabaseProvider.get_connection", return_value=None)
    def test_execute_query_returns_empty_on_no_conn(self, mock_conn):
        service = BaseService()
        result = service.execute_query("FULLDATA", "SELECT 1")
        assert result == []


class TestSearchService:
    def test_search_builds_correct_query(self):
        service = SearchService()
        with (
            patch.object(service, "execute_query", return_value=[]) as mock_query,
            patch.object(service, "save_to_csv", return_value="test.csv"),
        ):
            service.search({"AD": "AHMET"})
            call_args = mock_query.call_args
            assert "109m" in call_args[0][1]
            assert "AD = %s" in call_args[0][1]

    def test_search_birth_year_4digit(self):
        service = SearchService()
        with (
            patch.object(service, "execute_query", return_value=[]) as mock_query,
            patch.object(service, "save_to_csv", return_value="test.csv"),
        ):
            service.search({"DOGUMTARIHI": "1990"})
            call_args = mock_query.call_args
            assert "LEFT(DOGUMTARIHI, 4) = %s" in call_args[0][1]

    def test_search_like_condition(self):
        service = SearchService()
        with (
            patch.object(service, "execute_query", return_value=[]) as mock_query,
            patch.object(service, "save_to_csv", return_value="test.csv"),
        ):
            service.search({"AD": "%AHMET%"})
            call_args = mock_query.call_args
            assert "LIKE" in call_args[0][1]

    def test_search_empty_conditions(self):
        service = SearchService()
        with (
            patch.object(service, "execute_query", return_value=[]),
            patch.object(service, "save_to_csv", return_value="test.csv"),
        ):
            _, count, _ = service.search({})
            assert count == 0


class TestFamilyService:
    def test_get_full_person_invalid_tc(self):
        service = FamilyService()
        result = service.get_full_person("invalid")
        assert result is None

    def test_get_full_person_caches_result(self, sample_person_dict):
        service = FamilyService()
        mock_result = [sample_person_dict]
        with patch.object(service, "execute_query", side_effect=[mock_result, [], []]):
            p1 = service.get_full_person("12345678901")
            p2 = service.get_full_person("12345678901")
            assert p1 is p2

    def test_generate_tree_returns_not_found(self):
        service = FamilyService()
        with patch.object(service, "execute_query", return_value=[]):
            result = service.generate_tree("12345678901")
            assert result == "Kayıt bulunamadı."

    def test_fetch_gsm_numbers(self):
        service = FamilyService()
        with patch.object(service, "execute_query", return_value=[{"GSM": "532111"}, {"GSM": "533222"}]):
            result = service._fetch_gsm_numbers("12345678901")
            assert result == ["532111", "533222"]

    def test_fetch_gsm_numbers_empty(self):
        service = FamilyService()
        with patch.object(service, "execute_query", return_value=[]):
            result = service._fetch_gsm_numbers("12345678901")
            assert result == []
