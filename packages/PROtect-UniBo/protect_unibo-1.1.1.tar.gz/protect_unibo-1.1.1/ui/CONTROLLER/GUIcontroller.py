from ui.VIEW.GUIview import PasswordManagerView
from ui.MODEL.GUImodel import PasswordManagerModel
import tkinter as tk
from threading import Timer
from tkinter import filedialog
from project.add import computeMasterKey

class PasswordManagerController:
    def __init__(self, master_password=str):
        self.model=PasswordManagerModel()
        self.masterkey=computeMasterKey(master_password, "1")

        #Bind view callbacks to controller methods
        self.view=PasswordManagerView(
            on_add=self.add_entry,
            on_edit=self.edit_entry,
            on_delete=self.delete_entry,
            on_copy=self.copy_password,
            on_generate=self.generate_password,
            on_show=self.show_message,
            on_export=self.export_to_file,
            on_import=self.import_from_file,
            on_lock=self.lock_app,
        )
        self.view.pack(fill=tk.BOTH, expand=True)
        self.refresh_entries()

    def refresh_entries(self):
        entries=self.model.get_entries()
        self.view.set_entries(entries)

    #CRUD METHODS
    def add_entry(self):
        from tkinter.simpledialog import askstring
        site=askstring("Site", "Enter site name: ")
        url = askstring("URL", "Enter URL: ")
        email = askstring("Email", "Enter Email: ")
        username = askstring("Username", "Enter Username: ")
        password = askstring("Password", "Enter Password: ")
        if all([site, url, email, username, password]):
            self.model.add_entry(site, url, email, username, password, self.masterkey)
            self.refresh_entries()

    def edit_entry(self):
        selected=self.view.get_selected_entry()
        if not selected:
            return
        ID, Site, url, email, username, password = selected
        from tkinter.simpledialog import askstring
        new_site=askstring("Edit Site", "Site: ", initialvalue=Site)
        new_url=askstring("Edit URL", "URL: ", initialvalue=url)
        new_email=askstring("Edit Email", "Email: ", initialvalue=email)
        new_username=askstring("Edit Username", "Username: ", initialvalue=username)
        new_password=askstring("Edit Password", "Password (keep it empty to keep the current one): ")
        if not new_password:
            new_password=self.model.get_password(ID, self.masterkey)
        self.model.edit_entry(ID, new_site, new_url, new_email, new_username, new_password, self.masterkey)
        self.refresh_entries()

    def delete_entry(self):
        selected=self.view.get_selected_entry()
        if not selected:
            return
        ID=selected[0]
        self.model.delete_entry[ID]
        self.refresh_entries()

    #PASSWORD METHODS
    def copy_password(self):
        selected=self.view.get_selected_entry()
        if not selected:
            return
        ID=selected[0]
        pwd=self.model.get_password(ID, self.masterkey)
        if pwd:
            self.view.clipboard_clear()
            self.view.clipboard_append(pwd)
            self.view.show_message("Success", "Password copied to clipboard!")
    
    def show_password(self):
        selected=self.view.get_selected_entry()
        if not selected:
            return
        ID=selected[0]
        pwd=self.model.get_password(ID, self.masterkey)
        if pwd:
            top=tk.Toplevel(self.view)
            top.title("Password (10s)")
            lbl=tk.Label(top,text=pwd, font=("Helvetica", 14))
            lbl.pack(padx=20, pady=20)
            #Auto-close after 10 seconds for extra safety
            self.view.after(10000, top.destroy)
    

    #IMPORT/EXPORT
    def export_to_file(self):
        filepath=filedialog.asksaveasfilename(defaultextension=".cvs")
        if filepath:
            self.model.export_to_file(filepath,self.masterkey)
            self.view.show_message("Export", f"Entries exported to {filepath}")

    def import_from_file(self):
        filepath=filedialog.askopenfilename(filetypes=[("CVS Files", "*.cvs")])  
        if filepath:
            self.model.import_from_file(filepath, self.masterkey)
            self.view.show_message("Import", f"Entries imported from {filepath}")
    
    #LOCK
    def lock_app(self):
        self.model.close()
        self.masterkey=None
        self.view.clear_entries()
        self.view.show_message("Locked", "Password Manager Locked. Re-run to Unlock.")

    def show_message(self):
        pass
