import contextlib
import csv
import logging
import os
from contextlib import contextmanager
from typing import Any

from .database import DatabaseProvider
from .utils import is_valid_tc

WHERE_PARENTS = "ANNETC = %s OR BABATC = %s"


def build_query_condition(field: str, value: str) -> str:
    if field == "DOGUMTARIHI" and len(value) == 4 and value.isdigit():
        return "LEFT(DOGUMTARIHI, 4) = %s"
    if "%" in value:
        return f"{field} LIKE %s"
    return f"{field} = %s"


def build_parent_criteria(person) -> tuple[str, list]:
    clauses, params = [], []
    if is_valid_tc(person.ANNETC):
        clauses.append("ANNETC = %s")
        params.append(person.ANNETC)
    if is_valid_tc(person.BABATC):
        clauses.append("BABATC = %s")
        params.append(person.BABATC)
    if not clauses:
        return "", []
    criteria = f"({' OR '.join(clauses)}) AND TC != %s"
    params.append(person.TC)
    return criteria, params


class BaseService:
    """Ortak veritabanı işlemlerini içeren temel servis sınıfı."""

    @contextmanager
    def _get_connection(self, section: str):
        conn = DatabaseProvider.get_connection(section)
        if not conn:
            yield None
            return
        try:
            yield conn
        finally:
            with contextlib.suppress(Exception):
                conn.close()

    def execute_query(self, section: str, query: str, params: tuple = ()) -> list[dict]:
        with self._get_connection(section) as conn:
            if not conn:
                return []
            try:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()
            except Exception as e:
                level = logging.ERROR if section == "FULLDATA" else logging.WARNING
                logging.log(level, f"[{section}] Sorgu hatası: {e}\nSorgu: {query}")
                return []

    def execute_query_with_conn(
        self, conn, query: str, params: tuple = ()
    ) -> list[dict]:
        if not conn:
            return []
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logging.warning(f"Sorgu hatası: {e}\nSorgu: {query}")
            return []

    def save_to_csv(
        self,
        filename: str,
        header: list[str],
        rows: list[list[Any]],
        metadata: dict | None = None,
    ):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
            if metadata:
                writer.writerow([])
                for k, v in metadata.items():
                    writer.writerow([f"--- {k} ---", v])
        return filename
