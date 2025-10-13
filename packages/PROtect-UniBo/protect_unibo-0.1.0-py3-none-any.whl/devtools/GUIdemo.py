#demo for GUI to create an interactive exploration for visual/manual verification 
#It's not the TEST for GUI!
#demo does not need to be tested, we directly test the MVC in the tests package 

import ttkbootstrap as tb
from ui.VIEW.GUIview import PasswordManagerView

class DemoController:
    def __init__(self, view: PasswordManagerView):
        self.view=view
        self.entries=[
            ("GitHub", "https://github.com", "git@mail.com", "myuser", "password123"),
            ("Gmail", "https://gmail.com", "me@mail.com", "me", "secret456"),
        ]
        self.refresh()
    
    def refresh(self):
        self.view.set_entries(self.entries)
    
    def add(self): 
        self.entries.append(("NewSite", "https://new.com", "newuser@mail.com", "newuser", "mockpass"))
        self.refresh()
    
    def edit(self):
        sel=self.view.get_selected_entry()
        if sel:
            self.view.show_message("Edit", f"Would you edit {sel[0]}")
    
    def delete(self):
        sel=self.view.get_selected_entry()
        if sel:
            self.entries=[r for r in self.entries if r[0]!=sel[0]]
            self.refresh()
    
    def copy(self): 
        self.view.show_message("Copy", "Password copied (mock)")
    
    def show(self):
        self.view.show_message("Show", "Password123", kind="warning")
    
    def generate(self):
        self.view.show_message("Generate", "GenPassword!#")
    
    def export(self):
        self.view.show_message("Export", "Exported to demo.json")
    
    def import_(self):
        self.view.show_message("import", "Imported from demo.json")
    
    def lock(self):
        self.view.show_message("Lock", "Vault locked")
    
if __name__=="__main__":
    app=tb.Window(themename="vapor")

    controller_placeholder={}  # temp dict to hold real controller after creation
    def make_view():
        view=PasswordManagerView(
        app,
        on_add=lambda:controller_placeholder["ctrl"].add(),
        on_edit=lambda:controller_placeholder["ctrl"].edit(),
        on_delete=lambda:controller_placeholder["ctrl"].delete(),
        on_copy=lambda:controller_placeholder ["ctrl"].copy(),
        on_show=lambda:controller_placeholder ["ctrl"].show(),
        on_generate=lambda: controller_placeholder ["ctrl"].generate(),
        on_export=lambda:controller_placeholder ["ctrl"].export(),
        on_import=lambda:controller_placeholder ["ctrl"].import_(),
        on_lock=lambda:controller_placeholder ["ctrl"].lock()
        )
        return view
    view=make_view()
    ctrl = DemoController(view)
    controller_placeholder["ctrl"]=ctrl #injects the real controller
    view.pack(fill="both", expand=True)

    app.mainloop()