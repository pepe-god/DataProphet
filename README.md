# DataProphet
Python kullanarak SQL'den Türk vatandaşlarının kimlik bilgilerini çıkaran bir betik ve daha fazlası!
Kişiyi tespit ettikten sonra, hedef kişinin soy bilgilerine daha karmaşık olan soy ağacı betiğiyle ulaşın.

**İşinize yaradıysa yıldızlamayı unutmayın.**

## 1. ftree.py

Bu script, bir TC Kimlik Numarasına dayalı olarak bir aile ağı oluşturur ve bu ağı bir CSV dosyasına kaydeder. Script, MySQL veritabanına bağlanarak ilgili aile üyelerinin bilgilerini çeker ve bu bilgileri hiyerarşik bir şekilde düzenler. Kullanıcıdan bir TC Kimlik Numarası alınır ve bu numaraya dayalı olarak aile ağı oluşturulur. Aile üyeleri, anne, baba, çocuklar, kardeşler, yeğenler, dayı/teyze, amca/hala ve kuzenler gibi kategorilere ayrılır. Tüm bu bilgiler, kullanıcının adı ve soyadına dayalı bir CSV dosyasına kaydedilir.

## 2. searcher.py

Bu script, kullanıcının belirli kriterlere göre aile üyelerini aramasını sağlar ve sonuçları bir CSV dosyasına kaydeder. Script, kullanıcının istediği alanları doldurmasına veya boş bırakmasına izin vererek esnek bir arama yapmasını sağlar. Kullanıcı, TC Kimlik Numarası, ad, soyad, doğum yılı, nüfus ili, nüfus ilçesi, anne adı, anne TC'si, baba adı, baba TC'si ve uyruk gibi alanlardan istediğini doldurarak arama yapabilir. Sonuçlar, otomatik olarak oluşturulan bir CSV dosyasına kaydedilir ve kullanıcıya bilgi verilir.

## Bağımlılıklar

Bu scriptler için aşağıdaki bağımlılıkları yüklemeniz gerekmektedir:

### Python Standart Kütüphaneleri
- **csv**: CSV dosyalarını okumak ve yazmak için kullanılır.
- **logging**: Günlük kaydı için kullanılır.
- **configparser**: Yapılandırma dosyalarını okumak için kullanılır.
- **tkinter**: GUI oluşturmak için kullanılır (ikinci script için).

### Harici Kütüphaneler
- **mysql-connector-python**: MySQL veritabanına bağlanmak ve sorguları çalıştırmak için kullanılır.

### Bağımlılıkları Yüklemek İçin

#### Terminal
1. **mysql-connector-python**:
   ```bash
   pip install mysql-connector-python
##
A script that extracts Turkish citizens' identity information from SQL using Python and more!
Once you have identified the person, get the target person's genealogical information with the more complex family tree script.

**Don't forget to star if it worked for you.**

## 1. ftree.py

This script creates a family tree based on an ID number and saves it in a CSV file. The script connects to a MySQL database and pulls the information of the relevant family members and organizes this information in a hierarchical way. An ID number is obtained from the user and a family network is created based on this number. Family members are categorized as mother, father, children, siblings, nephews, nieces, nephews, uncles/aunts and cousins. All this information is saved in a CSV file based on the user's first and last name.

## 2. searcher.py

This script allows the user to search for family members based on specific criteria and saves the results in a CSV file. The script allows the user to perform a flexible search by allowing the user to fill in the desired fields or leave them blank. The user can search by filling in any of the fields such as Turkish ID Number, first name, last name, birth year, population province, population district, mother's name, mother's ID, father's name, father's ID and nationality. The results are saved in an automatically generated CSV file and the user is notified.

## Dependencies

You need to install the following dependencies for these scripts:

#### Python Standard Libraries
- **csv**: Used to read and write CSV files.
- **logging**: Used for logging.
- **configparser**: Used for reading configuration files.
- **tkinter**: Used to create GUI (for the second script).

### External Libraries
- **mysql-connector-python**: Used to connect to the MySQL database and run queries.

#### To Install Dependencies

#### Terminal
1. **mysql-connector-python**:
   ```bash
   pip install mysql-connector-python
