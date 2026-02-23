import configparser
import os
import logging

CONFIG_PATH = 'config.ini'

def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        logging.error(f"Yapılandırma dosyası bulunamadı: {CONFIG_PATH}")
    config.read(CONFIG_PATH)
    return config
