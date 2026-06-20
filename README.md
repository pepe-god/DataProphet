# DataProphet

Kişisel veri yönetim sistemi. MySQL veritabanından kişi ve ağaç bilgilerini sorgular, CSV'ye aktarır.

## Çalıştırma

```bash
uv sync
cp src/config.ini.example src/config.ini  # veritabanı bilgilerini doldur
uv run data       # ana uygulama
uv run old101     # 101 uygulaması
```
