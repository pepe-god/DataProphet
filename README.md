# DataProphet
Python kullanarak SQL'den Türk vatandaşlarının kimlik bilgilerini çıkaran bir betik ve daha fazlası!
Searcher ile kişiyi tespit ettikten sonra, hedef kişinin soy bilgilerine daha karmaşık olan soy ağacı betiğiyle ulaşın.

**İşinize yaradıysa yıldızlamayı unutmayın.**

## A+sulale.py Nasıl Çalışır
Bu Python betiği, belirli bir Türk Kimlik Numarasına (TC Kimlik No) sahip kişinin soy ağacını bir MySQL veritabanından alır ve bu bilgileri bir CSV dosyasına kaydeder. Betik, bir veritabanı bağlantısı oluşturur, kullanıcıdan bir TC Kimlik No ister, ilgili aile üyelerinin bilgilerini çeker ve bu bilgileri bir CSV dosyasına yazar. Ayrıca, soy ağacındaki çeşitli üyelerin sayılarını özet olarak CSV dosyasına kaydeder.

### Betiği Kullanmak İçin Gereken Önkoşullar
Betiği kullanmak için aşağıdaki önkoşullara ihtiyacınız vardır:

1. **Python Yüklü Olması**: Betik Python dili ile yazıldığından, sisteminizde Python'ın yüklü olması gerekmektedir. Python'ın en son sürümünü [Python resmi sitesinden](https://www.python.org/downloads/) indirebilirsiniz.

2. **MySQL Veritabanı**: Betik, bilgileri MySQL veritabanından çekmektedir. Bu nedenle, bir MySQL sunucunuzun olması ve `101m` adında bir veritabanının bulunması gerekmektedir. Veritabanınızda `101m` tablosu bulunmalı ve bu tablo, TC Kimlik No, ad, soyad, anne ve baba TC Kimlik No gibi alanları içermelidir.

3. **MySQL Connector Kütüphanesi**: Betik, MySQL veritabanına bağlanmak için `mysql-connector-python` kütüphanesini kullanır. Bu kütüphaneyi yüklemek için aşağıdaki komutu kullanabilirsiniz:
   ```bash
   pip install mysql-connector-python
   ```

4. **CSV Okuma/Yazma İzinleri**: Betik, sonuçları bir CSV dosyasına yazmaktadır. Bu nedenle, betiğin çalıştığı dizinde CSV dosyası oluşturma ve yazma izinlerinin olması gerekmektedir.

5. **Gerekli Bilgiler**: Betiği çalıştırırken, kullanıcıdan bir TC Kimlik No girmesi istenecektir. Bu TC Kimlik No'ya sahip kişinin veritabanınızda bulunması gerekmektedir.

Bu önkoşullar sağlandığında, betiği çalıştırarak belirtilen TC Kimlik No'ya sahip kişinin soy ağacını CSV dosyasına kaydedebilirsiniz.

----------

# DataProphet
A script for extracting the identity information of Turkish citizens from SQL using Python, and more!
After detecting the individual with the searcher, access their family tree information with the target individual query or the more complex family tree script.

**Don't forget to star it if it helps you.**

## How A+sulale.py Works
This Python script retrieves the family tree of a person with a specific Turkish Identification Number (TC Kimlik No) from a MySQL database and saves this information into a CSV file. The script establishes a database connection, prompts the user for a TC Kimlik No, fetches the relevant family members' information, and writes this information into a CSV file. Additionally, it summarizes the counts of various family members in the family tree and records these in the CSV file.

### Prerequisites for Using the Script
To use this script, you need the following prerequisites:

1. **Python Installation**: Since the script is written in Python, you need Python installed on your system. You can download the latest version of Python from the [official Python website](https://www.python.org/downloads/).

2. **MySQL Database**: The script retrieves information from a MySQL database. Therefore, you need to have a MySQL server and a database named `101m`. The database should contain a table named `101m` with fields such as TC Kimlik No, name, surname, mother's TC Kimlik No, and father's TC Kimlik No.

3. **MySQL Connector Library**: The script uses the `mysql-connector-python` library to connect to the MySQL database. You can install this library using the following command:
   ```bash
   pip install mysql-connector-python
   ```

4. **CSV Read/Write Permissions**: The script writes the results to a CSV file. Therefore, you need to have permissions to create and write CSV files in the directory where the script is run.

5. **Required Information**: When running the script, the user will be prompted to enter a TC Kimlik No. This TC Kimlik No must correspond to an individual present in your database.

Once these prerequisites are met, you can run the script to extract and save the family tree of the specified individual into a CSV file.
