import logging
import time
from datetime import datetime

from .models import DB_FIELDS_LIST
from .services import BaseService, build_query_condition
from .utils import clean_value


class SearchService(BaseService):
    def _build_conditions(
        self, conditions: dict[str, str]
    ) -> tuple[list[str], list[str]]:
        clauses, params = [], []
        for field, value in conditions.items():
            if not value:
                continue
            logging.debug(f"  [Kriter] {field}: {value}")
            clauses.append(build_query_condition(field, value))
            params.append(value)
        return clauses, params

    def _clean_results(self, results: list[dict]) -> list[list[str]]:
        rows = []
        for r in results:
            rows.append([clean_value(r.get(field, "")) for field in DB_FIELDS_LIST])
        return rows

    def search(self, conditions: dict[str, str]) -> tuple[str, int, float]:
        logging.info("--- Gelişmiş Arama Başlatıldı ---")
        clauses, params = self._build_conditions(conditions)

        where = " AND ".join(clauses) if clauses else "1=1"
        query = f"SELECT {', '.join(DB_FIELDS_LIST)} FROM `109m` WHERE {where}"

        logging.info("Sorgu veritabanına gönderiliyor...")
        start = time.monotonic()
        results = self.execute_query("FULLDATA", query, tuple(params))
        duration = time.monotonic() - start

        logging.info(
            f"Sorgu tamamlandı. {len(results)} kayıt bulundu. (Süre: {duration:.2f}s)"
        )

        rows = self._clean_results(results)

        filename = f"./index/search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        logging.info(f"Sonuçlar CSV dosyasına yazılıyor: {filename}")
        self.save_to_csv(filename, DB_FIELDS_LIST, rows, {"Toplam Kayıt": len(rows)})

        logging.info("--- Arama İşlemi Bitti ---")
        return filename, len(rows), duration
