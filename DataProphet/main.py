import logging
from core.gui import DataProphetApp

if __name__ == "__main__":
    # Loglama yapılandırması
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Uygulamayı başlat
    app = DataProphetApp()
    app.run()
