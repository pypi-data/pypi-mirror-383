from typing import Tuple, List, Optional
import mysql.connector
from project.dbconfig import dbconfig
from project.AES256util import encrypt, decrypt
from project.add import computeMasterKey

import os

test_mode = os.environ.get("TEST", "").lower() == "true"


QUERY_CREATE_DB = """
CREATE DATABASE IF NOT EXISTS PROtect
"""

QUERY_CREATE_TABLE_ENTRIES = """
CREATE TABLE IF NOT EXISTS PROtect.entries (
    ID int AUTO_INCREMENT PRIMARY KEY, 
    Site VARCHAR(255), 
    URL VARCHAR(225), 
    email VARCHAR(225), 
    username VARCHAR(225), 
    password VARBINARY(225)
)
"""

QUERY_CREATE_TABLE_SECRETS = """
CREATE TABLE IF NOT EXISTS PROtect.secrets (
    username VARCHAR(255) PRIMARY KEY,
    mp VARCHAR(225), 
    ds VARCHAR(225)
)
"""

class PasswordManagerModel:
    #Establish DB connection
    def __init__(self):
        self.db = dbconfig()
        self.cursor = self.db.cursor()
        self.__init__schema()

    def __init__schema(self):
        if test_mode:
            print("Test mode: cleaning up database PROtect")
            self.cursor.execute("DROP DATABASE PROtect;")
        #Create DB/tables if they don't exist yet (first-time configuration)
        self.cursor.execute(QUERY_CREATE_DB)
        self.cursor.execute(QUERY_CREATE_TABLE_ENTRIES)    
        self.cursor.execute(QUERY_CREATE_TABLE_SECRETS)
        self.db.commit()
    
    #CRUD OPERATIONS - Create, Read, Update, Delete
    def get_entries(self) -> List[Tuple[int,str,str,str,str]]: #returns all stored entries w/out password for security aims
        self.cursor.execute("SELECT ID, Site, URL, Email, Username FROM PROtect.entries")
        return self.cursor.fetchall() 
    
    def add_entry(self, Site, URL, Email, Username, password, masterkey):
        enc_pass=encrypt(password, masterkey)
        self.cursor.execute("INSERT INTO PROtect.entries (Site, URL, Email, Username, password) VALUES (%s,%s,%s,%s,%s)", (Site, URL, Email, Username, enc_pass))
        self.db.commit()
    
    def edit_entry(self, ID, Site, URL, Email, Username, password, masterkey): #Update entry (and/or encrypt new password)
        enc_pass=encrypt(password, masterkey)
        self.cursor.execute("UPDATE passwords SET Site=%s, URL=%s, Email=%s, Username=%s, password=%s WHERE ID=%s", (Site, URL, Email, Username, enc_pass, ID))
        self.db.commit()
    
    def delete_entry(self, ID):
        self.cursor.execute("DELETE FROM PROtect.entries WHERE ID=%s", (ID,))
        self.db.commit()
    
    def get_password(self, ID, masterkey) -> Optional[str]:
        self.cursor.execute("SELECT password FROM PROtect.entries WHERE ID=%s", (ID,))
        result=self.cursor.fetchone()
        if result:
            return decrypt(result[0], masterkey)
        return None
    
    def close(self):
        self.cursor.close()
        self.db.close()

    
    #Import/Export operations 
    def export_to_file(self, filepath:str, masterkey=bytes):
        #Export entries to a simple CSV file (Comma-Separated Values) decrypting passwords first
        import csv
        self.cursor.execute("SELECT ID, Site, URL, Email, Username, password FROM PROtect.entries")
        rows=self.cursor.fetchall()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Site", "URL", "Email", "Username", "password_encrypted"])
            for r in rows:
                writer.writerows([r[0],r[1],r[2],r[3],r[4],r[5]])
    
    def import_from_file(self, filepath:str, masterkey=bytes):
        import csv
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) == 6:
                    enc_pass=encrypt(masterkey, row[5])
                    self.cursor.execute("INSERT INTO PROtect.entries (ID, Site, URL, Email, Username, password) VALUES (%s,%s,%s,%s,%s,%s)", (row[0],row[1],row[2],row[3],row[4],enc_pass))
                    self.db.commit()
    
    


