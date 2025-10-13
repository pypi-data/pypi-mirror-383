import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

class Loginview(tb.Frame):
    def __init__(self, master, on_login, on_signup, **kwargs):
        super().__init__(master, padding=20, **kwargs)
        self.on_login = on_login
        self.on_signup = on_signup

        header = tb.Frame(self)
        header.pack(fill="x", pady=(0, 12))
        tb.Label(header, text="PROtect — Login", font=("Helvetica", 20)).pack(side="left")

        form = tb.Frame(self)
        form.pack(fill="x", pady=8)

        tb.Label(form, text="Username:", font=("Helvetica", 11)).pack(anchor="w")
        self.username_entry = tb.Entry(form)
        self.username_entry.pack(fill="x", pady=(4, 8))

        tb.Label(form, text="Master Password:", font=("Helvetica", 11)).pack(anchor="w")
        self.password_entry = tb.Entry(form, show="•")
        self.password_entry.pack(fill="x", pady=(4, 12))

        btns = tb.Frame(self)
        btns.pack(pady=6)
        tb.Button(btns, text="Login", bootstyle=PRIMARY, command=self._try_login).pack(side="left", padx=6)
        tb.Button(btns, text="Sign up", bootstyle=SUCCESS, command=self._try_signup).pack(side="left", padx=6)

        self.master.bind("<Return>", lambda e: self._try_login()) #allow ENTER to submit login via keyboard

        self.username_entry.focus()

    def _try_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Input required", "Please enter both username and master password.")
            return
        self.on_login(username, password)
    
    def _try_signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Input required", "Please provide a username and a master password to sign up.")
            return
        self.on_signup(username, password)

    def clear_password(self):
        self.password_entry.delete(0, tk.END)