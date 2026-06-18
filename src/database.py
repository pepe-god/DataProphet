import logging
from typing import ClassVar

import mysql.connector.pooling

from .config import load_config


class DatabaseProvider:
    """Veritabanı bağlantı havuzlarını yöneten ortak sağlayıcı."""

    _pools: ClassVar[dict] = {}
    _config: ClassVar[dict | None] = None

    @classmethod
    def _get_config(cls):
        if cls._config is None:
            cls._config = load_config()
        return cls._config

    @classmethod
    def get_pool(cls, section: str) -> mysql.connector.pooling.MySQLConnectionPool | None:
        if section not in cls._pools:
            config = cls._get_config()
            if section not in config:
                return None

            db_params = dict(config[section])
            try:
                cls._pools[section] = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name=f"{section}_pool", pool_size=10, pool_reset_session=True, **db_params
                )
                logging.info(f"'{section}' için bağlantı havuzu oluşturuldu.")
            except Exception:
                logging.exception(f"'{section}' havuzu oluşturulurken hata")
                return None

        return cls._pools[section]

    @classmethod
    def get_connection(cls, section: str):
        pool = cls.get_pool(section)
        return pool.get_connection() if pool else None
