import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import BOTH, X, Y, LEFT, RIGHT, messagebox
from typing import Callable, Optional, List, Tuple

class PasswordManagerView (tb.Frame):
    #It only defines the GUI, doesn't consider db, crypto etc. The controller must be passed in to handle actions
    def __init__(
        self,
        on_add: Callable[[], None] = lambda: None,
        on_edit: Callable[[], None] = lambda: None,
        on_delete: Callable[[], None] = lambda: None,
        on_copy: Callable[[], None] = lambda: None,
        on_show: Callable[[], None] = lambda: None,
        on_export: Callable[[], None] = lambda: None,
        on_import: Callable[[], None] = lambda: None,
        on_lock: Callable[[], None] = lambda: None,
        **kwargs
    ):
        super().__init__(padding=15, **kwargs)
    
        #HEADER
        header=tb.Frame(self)
        header.pack(fill=X)
        tb.Label(header, text="Password Manager", font=('Helvetica', 18)).pack(side=LEFT)
        tb.Button(header, text="Lock", bootstyle=DANGER, command=on_lock).pack(side=RIGHT, padx=5)
        tb.Button(header, text="Export", command=on_export).pack(side=RIGHT, padx=5)
        tb.Button(header, text="Import", command=on_import).pack(side=RIGHT, padx=5)

        #TOOLBAR
        bar=tb.Frame(self)
        bar.pack(fill=X, pady=8)
        tb.Button(bar, text="Add", bootstyle=SUCCESS, command=on_add).pack(side=LEFT, padx=4)
        tb.Button(bar, text="Edit", command=on_edit).pack(side=LEFT, padx=4)
        tb.Button(bar, text="Delete", bootstyle=DANGER, command=on_delete).pack(side=LEFT, padx=4)
        tb.Separator(bar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=8)
        tb.Button(bar, text="Copy", command=on_copy).pack(side=LEFT, padx=4)
        tb.Button(bar, text="Show (10s)", bootstyle=WARNING, command=on_show).pack(side=LEFT, padx=4)
        tb.Separator(bar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=8)

        #TABLE
        cols=("Site", "URL", "Email", "Username")
        self.tree=tb.Treeview(self, columns=cols, show="headings", height=14, bootstyle=INFO)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=180 if c=="URL" else 140)
        self.tree.pack(fill=BOTH, expand=True)

    #Public Methods to update UI
    def clear_entries(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
    
    def set_entries(self, rows:List[Tuple[str,str,str,str]]):
        #rows is the list of tuple with site, URL, email, username, so they are all strings
        self.clear_entries()
        for r in rows:
            self.tree.insert("", "end", values=r)

    def get_selected_entry(self) -> Optional[Tuple[str,str,str,str]]:
        sel=self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a row.")
            return None
        return self.tree.item(sel[0])["values"]
    
    def show_message(self, title:str, msg:str, kind="info"):
        if kind=="info":
            messagebox.showinfo(title, msg)
        elif kind=="error":
            messagebox.showerror(title, msg)
        elif kind=="warning":
            messagebox.showwarning(title,msg)
    
