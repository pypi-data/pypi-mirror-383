from dbconfig import dbconfig #needed to establish connection with the database
from add import computeMasterKey

#modules to be used in order to display the search results in a table-shaped format to the user
from rich import print as printc
from rich.console import Console
from rich.table import Table

import AES256util
import pyperclip

def retrieveEntries(mp, ds, search, decryptPassword = False):
    #search will contain the search fields that are inputted by the user and that we want to search in the database
    #decryptPassword is set to False for security reasons: it will be set to True only if the user explicitly wants it
    #if True, it will initiate the decryption operation on the needed password
    db = dbconfig()
    cursor = db.cursor()

    query = "" #two cases to be considered: the user might either query the database without specifying any search field, or doing it instead.

    if not search:
        query = "SELECT * FROM PROtect.entries"
        cursor.execute(query)
    else: 
        conditions=[]
        values=[]
        for field, value in search.items():
            conditions.append(f"{field}=%s")
            values.append(value)
        query=f"SELECT * FROM PROtect.entries WHERE {' AND '.join(conditions)}"
        cursor.execute(query, tuple(values))

    cursor.execute(query)
    results = cursor.fetchall()

    if len(results) == 0: 
        printc("[yellow][-][/yellow] No results for the search")
        return

    if (decryptPassword and len(results)>1) or (not decryptPassword):
        if decryptPassword:
            printc("[yellow][-][/yellow] More than one result found from the search, therefore not extracting the password. Please, be more specific")
        #handling the columns of the results table
        table = Table(title="Results")
        table.add_column("Site Name")
        table.add_column("URL")
        table.add_column("Email")
        table.add_column("Username")
        table.add_column("Password")

        #handling the rows of the results table
        for i in results: 
            table.add_row(i[0],i[1],i[2],i[3], "{hidden}") #the final field for the password is kept hidden because we don't want to show the password immediately, not even in its encrypted form

        console = Console()
        console.print(table)
        db.close()
        return

    if len(results)==1 and decryptPassword:
        #handling the case in which the user wants to access or copy the password to the clipboard
        #since the user also wants to see the password as decrypted, we would also have to actually decrypt the retrieved password 
        #in order to do this, we need the mp, the ds, and the mk. Since we've already included the values for mp and ds as arguments to our function,
        #we would just have to compute the mk and hence decrypt the password. This is done vie the same function that are used in the add.py file. 
        mk = computeMasterKey(mp,ds)
        decrypted = AES256util.decrypt(key=mk, source=results[0][4], keyType = "bytes")

        pyperclip.copy(decrypted.decode()) #this module is used to copy the decrypted password to the clipboard, after it has been decrypted and decoded
        printc("[green][+][/green] Password copied to clipboard")

    db.close()
