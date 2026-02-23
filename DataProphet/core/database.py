import logging
from core.config import load_config
import mysql.connector.pooling

class DatabaseProvider:
    """Veritabanı bağlantı havuzlarını yöneten ortak sağlayıcı."""
    
    _pools = {}

    @classmethod
    def get_pool(cls, section: str) -> Optional[mysql.connector.pooling.MySQLConnectionPool]:
        if section not in cls._pools:
            config = load_config()
            if section not in config:
                # Sessizce None dön, hata fırlatma
                return None
            
            db_params = dict(config[section])
            try:
                cls._pools[section] = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name=f"{section}_pool",
                    pool_size=10,
                    pool_reset_session=True,
                    **db_params
                )
                logging.info(f"'{section}' için bağlantı havuzu oluşturuldu.")
            except Exception as e:
                logging.error(f"'{section}' havuzu oluşturulurken hata: {e}")
                return None
        
        return cls._pools[section]

    @classmethod
    def get_connection(cls, section: str):
        pool = cls.get_pool(section)
        return pool.get_connection() if pool else None
