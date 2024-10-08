# DataProphet
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
