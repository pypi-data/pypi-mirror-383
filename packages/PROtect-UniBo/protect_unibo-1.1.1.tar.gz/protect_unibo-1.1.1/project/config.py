from getpass import getpass
import string
import random
import hashlib
import sys

from project.dbconfig import dbconfig 

from rich import print as printc 
from rich.console import Console

console = Console()

def checkConfig(): 
    db = dbconfig()
    cursor = db.cursor()
    query = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA  WHERE SCHEMA_NAME = 'PROtect'"
    cursor.execute(query)
    results = cursor.fetchall()
    db.close()
    if len(results)!=0:
        return True
    return False

def generateDeviceSecret(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))

def config(master_password=None):
    if checkConfig():
        printc("[red][!] Already Configured! [/red]")
        return 
    printc("[green][+] Creating new config [/green]")

    #Create Database
    db=dbconfig() 
    cursor=db.cursor()
    try: 
        cursor.execute("CREATE DATABASE PROtect")
    except Exception as e: 
        printc("[red][!] An error occurred while trying to create db. Maybe it already exists?")
        console.print_exception(show_locals=True)
    printc("[green][+][/green] Database 'PROtect' created")

    #create tables
    query = "CREATE TABLE PROtect.secrets (masterpassword_hash TEXT NOT NULL, device_secret TEXT NOT NULL)" 
    cursor.execute(query) 
    printc("[green][+][/green] Table 'secrets' created")

    query = "CREATE TABLE PROtect.entries (ID INT AUTO_INCREMENT PRIMARY KEY, sitename TEXT NOT NULL, siteurl TEXT NOT NULL, email TEXT, username TEXT, password TEXT NOT NULL)" 
    cursor.execute(query) 
    printc("[green][+][/green] Table 'entries' created")

    mp=""
    printc("[green][+] A [bold]MASTER PASSWORD[/bold] is the only password you will need to remember in-order to access all " \
    "your other passwords. Choosing a strong [bold]MASTER PASSWORD[/bold] is essential because all your other passwords will be " \
    "[bold]encrypted[/bold] with a key that is derived from your [bold]MASTER PASSWORD[/bold]. Therefore, please choose a strong " \
    "one that has upper and lower case characters, numbers and also special characters. " \
    "Remember your [bold]MASTER PASSWORD[/bold] because it won't be stored anywhere by this program, and you also cannot " \
    "change it once chosen. [/green]\n")
    while 1:
        mp=getpass("Choose a MASTER PASSWORD: ")
        if mp==getpass("Write the password again: ") and mp!="":
            break
        printc("[yellow][-] Please try again [/yellow]") 
        
    #Hash the MASTER PASSWORD
    hashed_mp = hashlib.sha256(mp.encode()).hexdigest()
    printc("[green][+][/green] Generated hash of the Master Password")
    
    #Generation of DEVICE SECRET 
    ds = generateDeviceSecret() 
    printc("[green][+][/green] Device Secret generated")

    #Add values into the database in the secrets table
    query = "INSERT INTO PROtect.secrets (masterpassword_hash, device_secret) values (%s, %s)"
    val = (hashed_mp, ds)
    cursor.execute(query, val) 
    db.commit()
    printc("[green][+][/green] Added to the database PROtect")
    printc("[green][+] Configuration completed! [/green]")

    db.close()

def delete():
    printc("[red][-] Deleting a config clears the device secret and all your entries from the database. " \
    "This means you will loose access to all your passwords that you have added into the password manager until now. " \
    "Only do this if you truly want to 'destroy' all your entries. This action cannot be undone. [/red]")

    while 1:
        op = input("Are you sure you want to continue? (y/N): ")
        if op.upper() == "Y":
          break
        if op.upper() == "N" or op.upper == "":
          sys.exit(0)
        else:
          continue

    printc("[green][-][/green] Deleting config")
    
    if not checkConfig():
        printc("[yellow][-][/yellow] No configuration exists to delete!")
        return
    
    db = dbconfig()
    cursor = db.cursor()
    query="DROP DATABASE PROtect"
    cursor.execute(query)
    db.commit()
    db.close()
    printc("[green][+] Configuration Successfully Deleted![/green]")

def reconfig():
    printc("[green][+][/green] Remaking config")
    try:
        # Attempt to delete existing configuration
        delete()
        printc("[green][+][/green] Old configuration deleted successfully.")
    except Exception as e:
        printc("[red][!][/red] Failed to delete existing configuration.")
        console.print_exception(show_locals=True)
        return  # Stop if deletion failed to avoid inconsistent state

    try:
        # Attempt to create a fresh configuration
        config()
        printc("[green][+][/green] New configuration created successfully.")
    except Exception as e:
        printc("[red][!][/red] Failed to create new configuration.")
        console.print_exception(show_locals=True)
        return  # Stop to avoid partially configured state

if __name__=="__main__":
    config()

