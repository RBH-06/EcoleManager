import tkinter as tk
from tkinter import ttk, messagebox
from ui.permissions_editor import PermissionsEditor
from typing import Optional

from services.auth_service import list_users, list_roles, create_user, update_user_role, reset_user_password, delete_user, AuthError


class UserForm(ttk.Frame):
    def __init__(self, master, on_saved):
        super().__init__(master, style="Card.TFrame", padding=16)
        self.on_saved = on_saved
        self.user_id: Optional[int] = None
        self._build()

    def _build(self):
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Fiche Utilisateur", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,8))

        ttk.Label(self, text="Nom d'utilisateur").grid(row=1, column=0, sticky="w", pady=4)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self, textvariable=self.username_var)
        self.username_entry.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(self, text="Rôle").grid(row=2, column=0, sticky="w", pady=4)
        self.role_combo = ttk.Combobox(self, state="readonly")
        self.role_combo.grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(self, text="Mot de passe (nouveau)").grid(row=3, column=0, sticky="w", pady=4)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=3, column=1, sticky="ew", pady=4)

        # Permissions editor
        self.perms = PermissionsEditor(self, title="Permissions Subadmin")
        self.perms.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8,0))

        btns = ttk.Frame(self)
        btns.grid(row=5, column=0, columnspan=2, sticky="e", pady=(8,0))
        ttk.Button(btns, text="Annuler", command=self._reset).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Enregistrer", style="Primary.TButton", command=self._save).grid(row=0, column=1)

        self._load_roles()

    def _load_roles(self):
        all_roles = list_roles()
        # Filter to only show Admin and Subadmin roles
        allowed_roles = ["Admin", "Subadmin"]
        roles = [r for r in all_roles if r["name"] in allowed_roles]
        
        self._roles = roles
        self.role_combo["values"] = [r["name"] for r in roles]
        if roles:
            self.role_combo.current(0)

    def load_user(self, user_id: int, data: dict):
        self.user_id = user_id
        self.username_var.set(data.get("username", ""))
        # set role combo
        names = [r["name"] for r in self._roles]
        try:
            idx = names.index(data.get("role"))
            self.role_combo.current(idx)
        except ValueError:
            if names:
                self.role_combo.current(0)
        self.password_var.set("")
        # permissions snapshot if present in list data
        perms = {
            "can_manage_students": data.get("can_manage_students", 0),
            "can_manage_classes": data.get("can_manage_classes", 0),
            "can_manage_attendance": data.get("can_manage_attendance", 0),
            "can_manage_fees": data.get("can_manage_fees", 0),
            "can_manage_users": data.get("can_manage_users", 0),
        }
        self.perms.set_permissions(perms)
        # when editing, lock username entry
        self.username_entry.configure(state="disabled")

    def _reset(self):
        self.user_id = None
        self.username_entry.configure(state="normal")
        self.username_var.set("")
        self.password_var.set("")
        if self._roles:
            self.role_combo.current(0)
        self.perms.set_permissions({})

    def _save(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        role_idx = self.role_combo.current()
        role_id = self._roles[role_idx]["id"] if role_idx >= 0 and role_idx < len(self._roles) else None
        
        # Enhanced validation
        from utils.validation import validate_username, validate_password_with_username
        
        # Validate username
        username_valid, username_errors = validate_username(username)
        if not username_valid:
            messagebox.showerror("Nom d'utilisateur invalide", "\n".join(username_errors))
            return
        
        if role_id is None:
            messagebox.showwarning("Champs requis", "Le rôle est obligatoire.")
            return
        
        try:
            # collect permissions only for Subadmin role
            selected_role = self._roles[role_idx]["name"] if role_idx >= 0 else ""
            perms_dict = self.perms.get_permissions() if selected_role == "Subadmin" else None
            
            if self.user_id:
                # update role (+ permissions); reset password if provided
                if password:
                    # Validate password for updates
                    password_valid, password_errors = validate_password_with_username(password, username)
                    if not password_valid:
                        messagebox.showerror("Mot de passe invalide", "\n".join(password_errors))
                        return
                    reset_user_password(self.user_id, password)
                
                update_user_role(self.user_id, role_id, permissions=perms_dict)
            else:
                if not password:
                    messagebox.showwarning("Champs requis", "Mot de passe requis pour la création.")
                    return
                
                # Validate password for new users
                password_valid, password_errors = validate_password_with_username(password, username)
                if not password_valid:
                    messagebox.showerror("Mot de passe invalide", "\n".join(password_errors))
                    return
                
                create_user(username, password, role_id, permissions=perms_dict)
            
            messagebox.showinfo("Succès", "Utilisateur enregistré.")
            self.on_saved()
        except AuthError as e:
            messagebox.showerror("Erreur", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


class UsersList(ttk.Frame):
    def __init__(self, master, on_select):
        super().__init__(master, style="Card.TFrame", padding=16)
        self.on_select = on_select
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text="Utilisateurs", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        search = ttk.Frame(self)
        search.grid(row=1, column=0, sticky="ew", pady=(8,8))
        search.columnconfigure(1, weight=1)
        ttk.Label(search, text="Recherche").grid(row=0, column=0, sticky="w")
        self.query_var = tk.StringVar()
        entry = ttk.Entry(search, textvariable=self.query_var)
        entry.grid(row=0, column=1, sticky="ew", padx=8)
        entry.bind("<Return>", lambda e: self._reload())
        ttk.Button(search, text="Rechercher", command=self._reload).grid(row=0, column=2)

        cols = ("id", "username", "role")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12, style="Modern.Treeview")
        headers = {"id": "ID", "username": "Nom d'utilisateur", "role": "Rôle"}
        for c in cols:
            self.tree.heading(c, text=headers[c], anchor="w")
            self.tree.column(c, anchor="w", width=140)
        self.tree.grid(row=2, column=0, sticky="nsew")
        self.rowconfigure(2, weight=1)

        # Note: we keep permissions in tree item data only (not visible). When loading a user,
        #       we pass those values from the list_users result to the form.

        actions = ttk.Frame(self)
        actions.grid(row=3, column=0, sticky="e", pady=(8,0))
        ttk.Button(actions, text="Nouveau", style="Primary.TButton", command=self._new).grid(row=0, column=0, padx=4)
        ttk.Button(actions, text="Modifier", command=self._edit).grid(row=0, column=1, padx=4)
        ttk.Button(actions, text="Supprimer", command=self._delete).grid(row=0, column=2)

        self._reload()

    def _reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = self.query_var.get().strip()
        for u in list_users(query=query):
            # Store permissions in item tags or values is limited; use iid mapping via set of columns not shown.
            self.tree.insert("", "end", iid=u["id"], values=(u["id"], u["username"], u["role"]))
            # Attach permissions in the item dict so we can retrieve them later
            item = self.tree.item(u["id"])  # returns dict; we add a transient key
            item["perms"] = {
                "can_manage_students": u.get("can_manage_students", 0),
                "can_manage_classes": u.get("can_manage_classes", 0),
                "can_manage_attendance": u.get("can_manage_attendance", 0),
                "can_manage_fees": u.get("can_manage_fees", 0),
                "can_manage_users": u.get("can_manage_users", 0),
            }
            # tkinter Treeview doesn't persist custom keys; keep an internal dict
            if not hasattr(self, "_perms_cache"):
                self._perms_cache = {}
            self._perms_cache[u["id"]] = item["perms"]

    def _selected_id(self) -> Optional[int]:
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _new(self):
        self.on_select(None)

    def _edit(self):
        uid = self._selected_id()
        if uid is None:
            messagebox.showinfo("Info", "Sélectionnez un utilisateur.")
            return
        self.on_select(uid)

    def _delete(self):
        uid = self._selected_id()
        if uid is None:
            messagebox.showinfo("Info", "Sélectionnez un utilisateur.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer cet utilisateur ?"):
            return
        try:
            delete_user(uid)
            self._reload()
        except AuthError as e:
            messagebox.showerror("Erreur", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


class UsersView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)

        self.list_panel = UsersList(self, on_select=self._on_select)
        self.list_panel.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        self.form_panel = UserForm(self, on_saved=self._on_saved)
        self.form_panel.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)

    def _on_select(self, user_id: Optional[int]):
        if user_id:
            # fetch data from list (username, role, permissions)
            item = self.list_panel.tree.item(str(user_id))
            vals = item.get("values", [])
            perms = getattr(self.list_panel, "_perms_cache", {}).get(user_id, {})
            if vals:
                data = {"username": vals[1], "role": vals[2], **perms}
                self.form_panel.load_user(user_id, data)
        else:
            self.form_panel._reset()

    def _on_saved(self):
        self.list_panel._reload()