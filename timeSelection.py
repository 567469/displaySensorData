import tkinter as tk
from tkinter import Toplevel, Listbox

class SelectionDialog(Toplevel):
    def __init__(self, parent, options):
        super().__init__(parent)
        self.title("Auswahl Dialog")
        self.options = options
        self.geometry("500x500")
        self.result = None

        self.listbox = Listbox(self)
        self.listbox.pack(padx=20, pady=20, fill="both", expand=True)

        for option in options:
            self.listbox.insert("end", option)

        select_button = tk.Button(self, text="Auswählen", command=self.on_select)
        select_button.pack(pady=10)

    def on_select(self):
        try:
            index = self.listbox.curselection()
            self.result = self.options[index[0]]
            self.destroy()
        except IndexError:
            # Nothing was selected
            pass

    def show(self):
        self.wait_window()
        return self.result