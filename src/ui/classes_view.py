import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict

from services.class_service import (
    list_classes,
    list_classes_with_enrollment_count,
    create_class,
    update_class,
    delete_class,
    enroll_student,
    unenroll_student,
    list_enrolled_students,
)
from services.student_service import list_students
from ui.enrollment_dialog import EnrollmentDialog
from ui.attendance_dialog import AttendanceDialog


class ClassForm(ttk.Frame):
    def __init__(self, master, on_saved):
        super().__init__(master, style="Card.TFrame", padding=16)
        self.on_saved = on_saved
        self.class_id: Optional[int] = None
        self._build()

    def _build(self):
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Fiche Classe", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,8))
        fields = [
            ("Nom", "name"),
            ("Niveau", "level"),
            ("Section", "section"),
            ("Salle", "room"),
            ("Année scolaire (ex: 2024-2025)", "academic_year"),
        ]
        self.vars = {}
        r = 1
        for label, key in fields:
            ttk.Label(self, text=label).grid(row=r, column=0, sticky="w", pady=4)
            var = tk.StringVar()
            self.vars[key] = var
            ttk.Entry(self, textvariable=var).grid(row=r, column=1, sticky="ew", pady=4)
            r += 1

        actions = ttk.Frame(self)
        actions.grid(row=r, column=0, columnspan=2, sticky="e", pady=(8,0))
        ttk.Button(actions, text="Annuler", command=self._reset).grid(row=0, column=0, padx=4)
        ttk.Button(actions, text="Enregistrer", style="Primary.TButton", command=self._save).grid(row=0, column=1)

    def load_class(self, class_id: int, data: dict):
        self.class_id = class_id
        for k, v in self.vars.items():
            v.set(data.get(k, "") or "")

    def _reset(self):
        self.class_id = None
        for v in self.vars.values():
            v.set("")

    def _save(self):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        if not data["name"] or not data["academic_year"]:
            messagebox.showwarning("Champs requis", "Nom et Année scolaire sont obligatoires.")
            return
        try:
            if self.class_id:
                update_class(self.class_id, data)
            else:
                self.class_id = create_class(data)
            messagebox.showinfo("Succès", "Classe enregistrée.")
            self.on_saved()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


class ClassesList(ttk.Frame):
    def __init__(self, master, on_select, permissions: Optional[Dict[str, int]] = None):
        super().__init__(master, style="Card.TFrame", padding=16)
        self.on_select = on_select
        self.permissions = permissions or {}
        self.selected_class_id = None  # Initialize selected_class_id
        self._build()

    def _build(self):
        # Main layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Search bar and action buttons
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(8, 0))
        top_frame.columnconfigure(1, weight=1)

        ttk.Label(top_frame, text="Rechercher:").grid(row=0, column=0, sticky="w")
        self.query_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.query_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(top_frame, text="Rechercher", style="Primary.TButton", command=self._reload).grid(row=0, column=2, padx=4)
        ttk.Button(top_frame, text="Nouvelle", style="Primary.TButton", command=self._new).grid(row=0, column=3, padx=4)
        ttk.Button(top_frame, text="Modifier", command=self._edit).grid(row=0, column=4, padx=4)
        ttk.Button(top_frame, text="Inscriptions", command=self._open_enrollment_for_selected).grid(row=0, column=5, padx=4)
        
        # Only show attendance button if user has permission
        if self.permissions.get("can_manage_attendance", False):
            ttk.Button(top_frame, text="Présences", command=self._open_attendance_for_selected).grid(row=0, column=6, padx=4)
            delete_column = 7
        else:
            delete_column = 6
            
        ttk.Button(top_frame, text="Supprimer", command=self._delete).grid(row=0, column=delete_column, padx=4)

        # Treeview for classes
        cols = ("id", "name", "level", "section", "room", "academic_year", "enrollment_count", "session_count")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20, style="Modern.Treeview")
        headers = {
            "id": "ID",
            "name": "Nom",
            "level": "Niveau",
            "section": "Section",
            "room": "Salle",
            "academic_year": "Année",
            "enrollment_count": "Élèves",
            "session_count": "Sessions",
        }
        for c in cols:
            self.tree.heading(c, text=headers[c], anchor="w")
            if c == "id":
                self.tree.column(c, width=60, anchor="w")
            elif c == "enrollment_count":
                self.tree.column(c, width=80, anchor="center")
            elif c == "session_count":
                self.tree.column(c, width=80, anchor="center")
            else:
                self.tree.column(c, width=120, anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(8, 8))
        self.tree.bind("<ButtonRelease-1>", self._on_class_select)  # Bind selection event
        self.tree.bind("<Button-3>", self._on_right_click)  # Bind right-click event

        self._reload()

    def _reload(self):
        # Clear existing rows in the tree view
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Fetch and display classes
        query = self.query_var.get().strip()
        try:
            classes = list_classes_with_enrollment_count(query=query)
            for row in classes:
                self.tree.insert("", "end", iid=row["id"], values=(
                    row["id"],
                    row["name"],
                    row["level"] or "",
                    row["section"] or "",
                    row["room"] or "",
                    row["academic_year"] or "",
                    row["enrollment_count"] or 0,
                    row["session_count"] or 0,
                ))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les classes: {str(e)}")

    def _selected_id(self) -> Optional[int]:
        s = self.tree.selection()
        return int(s[0]) if s else None

    def _new(self):
        self.on_select(None)

    def _edit(self):
        sid = self._selected_id()
        if sid is None:
            messagebox.showinfo("Info", "Sélectionnez une classe à modifier.")
            return
        self.on_select(sid)

    def _delete(self):
        sid = self._selected_id()
        if sid is None:
            messagebox.showinfo("Info", "Sélectionnez une classe à supprimer.")
            return
        if not messagebox.askyesno("Confirmation", "Confirmez-vous la suppression de cette classe ?"):
            return
        try:
            delete_class(sid)
            self._reload()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _on_class_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.selected_class_id = int(selected_item[0])  # Update selected_class_id
            # Notify the parent about the selection change
            self.on_select(self.selected_class_id)
            # Highlight the selected class
            self.tree.selection_set(selected_item[0])
        else:
            self.selected_class_id = None
            self.on_select(None)

    def get_selected_class_id(self):
        return self.selected_class_id

    def _on_right_click(self, event):
        """Handle right-click on class treeview"""
        # Get the item under cursor
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # Select the item if not already selected
        if item not in self.tree.selection():
            self.tree.selection_set(item)
            self.selected_class_id = int(item)
            self.on_select(self.selected_class_id)
        
        # Get class information
        class_id = int(item)
        class_values = self.tree.item(item)['values']
        class_name = class_values[1] if len(class_values) > 1 else f"Classe {class_id}"
        
        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Gérer les inscriptions", 
                               command=lambda: self._open_enrollment_dialog(class_id, class_name))
        
        # Only show attendance option if user has permission
        if self.permissions.get("can_manage_attendance", False):
            context_menu.add_command(label="Gérer les présences", 
                                   command=lambda: self._open_attendance_dialog(class_id, class_name))
        
        context_menu.add_separator()
        context_menu.add_command(label="Modifier", command=self._edit)
        context_menu.add_command(label="Supprimer", command=self._delete)
        
        # Show context menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _open_enrollment_dialog(self, class_id: int, class_name: str):
        """Open enrollment dialog for the selected class"""
        def on_enrollment_changed():
            # Refresh the main view if needed
            pass
        
        dialog = EnrollmentDialog(self, class_id, class_name, on_enrollment_changed)
        dialog.focus_set()  # Set focus to dialog

    def _open_attendance_dialog(self, class_id: int, class_name: str):
        """Open attendance dialog for the selected class"""
        # Check permission
        if not self.permissions.get("can_manage_attendance", False):
            messagebox.showwarning("Permission refusée", "Vous n'avez pas la permission de gérer les présences.")
            return
            
        def on_attendance_changed():
            # Refresh the main view if needed
            pass
        
        dialog = AttendanceDialog(self, class_id, class_name, on_attendance_changed)
        dialog.focus_set()  # Set focus to dialog

    def _open_enrollment_for_selected(self):
        """Open enrollment dialog for the currently selected class"""
        class_id = self._selected_id()
        if class_id is None:
            messagebox.showinfo("Info", "Veuillez sélectionner une classe d'abord.")
            return
        
        # Get class information
        item = self.tree.item(str(class_id))
        class_values = item.get("values", [])
        class_name = class_values[1] if len(class_values) > 1 else f"Classe {class_id}"
        
        self._open_enrollment_dialog(class_id, class_name)

    def _open_attendance_for_selected(self):
        """Open attendance dialog for the currently selected class"""
        # Check permission
        if not self.permissions.get("can_manage_attendance", False):
            messagebox.showwarning("Permission refusée", "Vous n'avez pas la permission de gérer les présences.")
            return
            
        class_id = self._selected_id()
        if class_id is None:
            messagebox.showinfo("Info", "Veuillez sélectionner une classe d'abord.")
            return
        
        # Get class information
        item = self.tree.item(str(class_id))
        class_values = item.get("values", [])
        class_name = class_values[1] if len(class_values) > 1 else f"Classe {class_id}"
        
        self._open_attendance_dialog(class_id, class_name)


class EnrollmentPanel(ttk.Frame):
    def __init__(self, master, get_selected_class_id):
        super().__init__(master, style="Card.TFrame", padding=16)
        self.get_selected_class_id = get_selected_class_id
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text="Inscriptions", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        # List enrolled students
        self.tree = ttk.Treeview(self, columns=("id", "enrollment_no", "name"), show="headings", height=10, style="Modern.Treeview")
        self.tree.heading("id", text="ID", anchor="w")
        self.tree.heading("enrollment_no", text="Matricule", anchor="w")
        self.tree.heading("name", text="Nom", anchor="w")
        self.tree.column("id", width=60, anchor="w")
        self.tree.column("enrollment_no", width=120, anchor="w")
        self.tree.column("name", width=200, anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(8,8))
        self.rowconfigure(1, weight=1)

        # Add student section
        form = ttk.Frame(self)
        form.grid(row=2, column=0, sticky="ew")
        form.columnconfigure(1, weight=1)
        ttk.Label(form, text="Ajouter élève").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.search_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(form, text="Rechercher", command=self._search_students).grid(row=0, column=2)

        self.results = ttk.Treeview(self, columns=("id", "enrollment_no", "name"), show="headings", height=6, style="Modern.Treeview")
        self.results.heading("id", text="ID", anchor="w")
        self.results.heading("enrollment_no", text="Matricule", anchor="w")
        self.results.heading("name", text="Nom", anchor="w")
        self.results.column("id", width=60, anchor="w")
        self.results.column("enrollment_no", width=120, anchor="w")
        self.results.column("name", width=200, anchor="w")
        self.results.grid(row=3, column=0, sticky="nsew", pady=(8,0))
        # Bind double-click to enroll
        self.results.bind("<Double-1>", lambda e: self._enroll())

        actions = ttk.Frame(self)
        actions.grid(row=4, column=0, sticky="e", pady=(8,0))
        ttk.Button(actions, text="Inscrire", style="Primary.TButton", command=self._enroll).grid(row=0, column=0, padx=4)
        ttk.Button(actions, text="Désinscrire", command=self._unenroll).grid(row=0, column=1)

    def reload_enrollments(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        cid = self.get_selected_class_id()
        if not cid:
            return
        for s in list_enrolled_students(cid):
            name = f"{s['last_name']} {s['first_name']}"
            self.tree.insert("", "end", iid=s["id"], values=(s["id"], s["enrollment_no"], name))

    def _search_students(self):
        for i in self.results.get_children():
            self.results.delete(i)
        q = self.search_var.get().strip()
        try:
            students = list_students(query=q)
            for s in students:
                name = f"{s['last_name']} {s['first_name']}"
                self.results.insert("", "end", iid=s["id"], values=(s["id"], s["enrollment_no"], name))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche d'élèves: {str(e)}")

    def _selected_result_id(self) -> Optional[int]:
        sel = self.results.selection()
        return int(sel[0]) if sel else None

    def _selected_enrolled_id(self) -> Optional[int]:
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _enroll(self):
        # Attempt to retrieve the selected class ID
        cid = self.get_selected_class_id()
        
        if cid is None:
            messagebox.showinfo("Info", "Veuillez sélectionner une classe d'abord.")
            return

        # Retrieve the selected student ID
        sid = self._selected_result_id()
        
        if sid is None:
            messagebox.showinfo("Info", "Veuillez sélectionner un élève dans la liste des résultats.")
            return

        # Validate both IDs
        if not cid or not sid:
            messagebox.showinfo("Info", "Choisissez une classe et un élève.")
            return

        # Attempt to enroll the student
        try:
            enroll_student(cid, sid)
            self.reload_enrollments()
            messagebox.showinfo("Succès", "Élève inscrit avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _unenroll(self):
        cid = self.get_selected_class_id()
        sid = self._selected_enrolled_id()
        if not cid or not sid:
            messagebox.showinfo("Info", "Sélectionnez un élève inscrit.")
            return
        try:
            unenroll_student(cid, sid)
            self.reload_enrollments()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


class ClassesView(ttk.Frame):
    def __init__(self, master, permissions: Optional[Dict[str, int]] = None):
        super().__init__(master)
        self.selected_class_id: Optional[int] = None
        self.permissions = permissions or {}
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)

        self.list_panel = ClassesList(self, on_select=self._on_select, permissions=self.permissions)
        self.list_panel.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        self.form_panel = ClassForm(self, on_saved=self._on_saved)
        self.form_panel.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)

        # Remove the enrollment panel - now using dialog approach
        # self.enroll_panel = EnrollmentPanel(self, get_selected_class_id=lambda: self.selected_class_id)
        # self.enroll_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=16, pady=(0,16))

        self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, weight=2)

    def _on_select(self, class_id: Optional[int]):
        self.selected_class_id = class_id
        if class_id:
            # load for edit: quick lookup from list widget's values
            item = self.list_panel.tree.item(str(class_id))
            vals = item.get("values", [])
            if vals:
                data = {
                    "name": vals[1],
                    "level": vals[2] or "",
                    "section": vals[3] or "",
                    "room": vals[4] or "",
                    "academic_year": vals[5] or "",
                }
                self.form_panel.load_class(class_id, data)
        else:
            self.form_panel._reset()
        # Remove enrollment panel reload since we're using dialog approach
        # self.enroll_panel.reload_enrollments()

    def _on_saved(self):
        self.list_panel._reload()