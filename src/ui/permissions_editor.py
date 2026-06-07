import tkinter as tk
from tkinter import ttk
from typing import Dict

PERM_FIELDS = [
    ("Gérer les élèves", "can_manage_students"),
    ("Gérer les classes", "can_manage_classes"),
    ("Gérer les présences (dans les classes)", "can_manage_attendance"),
    ("Gérer les frais", "can_manage_fees"),
    ("Gérer les utilisateurs", "can_manage_users"),
]

class PermissionsEditor(ttk.LabelFrame):
    def __init__(self, master, title: str = "Permissions"):
        super().__init__(master, text=title)
        self.vars: Dict[str, tk.BooleanVar] = {}
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        r = 0
        for label, key in PERM_FIELDS:
            var = tk.BooleanVar(value=False)
            self.vars[key] = var
            cb = ttk.Checkbutton(self, text=label, variable=var)
            cb.grid(row=r, column=0, sticky="w", padx=4, pady=2)
            r += 1

    def get_permissions(self) -> Dict[str, int]:
        return {k: int(v.get()) for k, v in self.vars.items()}

    def set_permissions(self, perms: Dict[str, int]):
        for k, v in perms.items():
            if k in self.vars:
                self.vars[k].set(bool(v))