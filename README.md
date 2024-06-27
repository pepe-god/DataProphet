# DataProphet
A script to extract Turkish citizens identity information from SQL with Python --- 

Python ile SQL'den Türk vatandaşlarının kimlik bilgilerini çıkarmak için bir betik ve daha fazlası :D

"Success is not final, failure is not fatal: It is the courage to continue that counts." - Winston Churchill

mysql.connector required // bu kütüpaneyi indirin

searcher ile kişiyi tespit ettikten sonra hedef kişiyi sorgu veya daha complex olan sulale betiğiyle soy bilgilerine ulaşın.

**İşinize yaradıysa yıldızlamayı unutmayın.**

A+sulale.py Nasıl Çalışır.
Bu Python scripti, belirli bir TC kimlik numarasına sahip kişinin aile ağacını MySQL veritabanından çeker ve bu bilgileri bir CSV dosyasına kaydeder. Script, veritabanı bağlantısı oluşturur, kullanıcıdan TC kimlik numarası alır, ilgili aile üyelerinin bilgilerini çeker ve bu bilgileri CSV dosyasına yazar. Ayrıca, aile ağacındaki çeşitli üyelerin sayılarını özet olarak CSV dosyasına kaydeder.

Bu scripti kullanabilmek için aşağıdaki önkoşullara ihtiyacınız vardır:

1. **Python Yüklü Olması**: Script Python dili ile yazıldığından, sisteminizde Python'ın yüklü olması gerekmektedir. Python'ın en son sürümünü [Python resmi sitesinden](https://www.python.org/downloads/) indirebilirsiniz.

2. **MySQL Veritabanı**: Script, bilgileri MySQL veritabanından çekmektedir. Bu nedenle, bir MySQL sunucunuzun olması ve `101m` adında bir veritabanının bulunması gerekmektedir. Veritabanınızda `101m` tablosu bulunmalı ve bu tablo, TC kimlik numarası, ad, soyad, anne ve baba TC kimlik numaraları gibi alanları içermelidir.

3. **MySQL Connector Kütüphanesi**: Script, MySQL veritabanına bağlanmak için `mysql-connector-python` kütüphanesini kullanır. Bu kütüphaneyi yüklemek için aşağıdaki komutu kullanabilirsiniz:
   ```bash
   pip install mysql-connector-python
   ```

4. **CSV Okuma/Yazma İzinleri**: Script, sonuçları bir CSV dosyasına yazmaktadır. Bu nedenle, scriptin çalıştığı dizinde CSV dosyası oluşturma ve yazma izinlerinin olması gerekmektedir.

5. **Gerekli Bilgiler**: Scripti çalıştırırken, kullanıcıdan bir TC kimlik numarası girmesi istenecektir. Bu TC kimlik numarasına sahip kişinin veritabanınızda bulunması gerekmektedir.

Bu önkoşullar sağlandığında, scripti çalıştırarak belirtilen TC kimlik numarasına sahip kişinin aile ağacını CSV dosyasına kaydedebilirsiniz.
