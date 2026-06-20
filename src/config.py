import configparser
import logging
import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SRC_DIR, "config.ini")


def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        logging.error(
            f"Yapılandırma dosyası bulunamadı: {CONFIG_PATH} — bazı özellikler çalışmayacak"
        )
        return config
    config.read(CONFIG_PATH)
    return config
