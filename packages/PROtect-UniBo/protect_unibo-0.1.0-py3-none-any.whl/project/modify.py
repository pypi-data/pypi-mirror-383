from rich import print as printc
from dbconfig import dbconfig
from add import computeMasterKey
import AES256util

def modify_entry(ID, site, url, email, username, password, mp, ds):
    #Modify one or more fields of an existing entry
    try:
        db = dbconfig()
        if not db:
            printc("[red][!] Could not connect to database[/red]")
            return

        cursor = db.cursor()

        mk = computeMasterKey(mp, ds)
        enc_pass = AES256util(password, mk)

        query = "UPDATE PROtect.entries SET Site=%s, URL=%s, Email=%s, Username=%s, password=%s WHERE ID=%s"
        cursor.execute(query, (site, url, email, username, enc_pass, ID))
        db.commit()
        printc(f"[green][+][/green] Entry with ID {ID} updated successfully")

    except Exception as e:
        printc(f"[red][!] Error updating entry: {e}[/red]")