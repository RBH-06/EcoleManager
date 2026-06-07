import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from services.student_service import list_students
from services.class_service import enroll_student, unenroll_student, list_enrolled_students


class EnrollmentDialog(tk.Toplevel):
    def __init__(self, parent, class_id: int, class_name: str, on_enrollment_changed: Optional[Callable] = None):
        super().__init__(parent)
        self.class_id = class_id
        self.class_name = class_name
        self.on_enrollment_changed = on_enrollment_changed
        
        # Configure dialog
        self.title(f"Inscriptions - {class_name}")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.center_window()
        
        self._build()
        self._load_enrolled_students()

    def center_window(self):
        """Center the dialog window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build(self):
        # Main container
        main_frame = ttk.Frame(self, padding="16")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Inscriptions - {self.class_name}", 
                               font=("Arial", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 16))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)
        
        # Tab 1: Enrolled Students
        enrolled_frame = ttk.Frame(notebook)
        notebook.add(enrolled_frame, text="Élèves Inscrits")
        self._build_enrolled_tab(enrolled_frame)
        
        # Tab 2: Add Students
        add_frame = ttk.Frame(notebook)
        notebook.add(add_frame, text="Ajouter des Élèves")
        self._build_add_tab(add_frame)

    def _build_enrolled_tab(self, parent):
        """Build the enrolled students tab"""
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(0, 8))
        
        ttk.Button(toolbar, text="Actualiser", command=self._load_enrolled_students).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="Désinscrire", command=self._unenroll_selected).pack(side="left")
        
        # Enrolled students treeview
        columns = ("id", "enrollment_no", "name", "enrolled_date")
        self.enrolled_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        self.enrolled_tree.heading("id", text="ID")
        self.enrolled_tree.heading("enrollment_no", text="Matricule")
        self.enrolled_tree.heading("name", text="Nom")
        self.enrolled_tree.heading("enrolled_date", text="Date d'inscription")
        
        self.enrolled_tree.column("id", width=60)
        self.enrolled_tree.column("enrollment_no", width=120)
        self.enrolled_tree.column("name", width=200)
        self.enrolled_tree.column("enrolled_date", width=120)
        
        # Scrollbar
        enrolled_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.enrolled_tree.yview)
        self.enrolled_tree.configure(yscrollcommand=enrolled_scrollbar.set)
        
        self.enrolled_tree.pack(side="left", fill="both", expand=True)
        enrolled_scrollbar.pack(side="right", fill="y")

    def _build_add_tab(self, parent):
        """Build the add students tab"""
        # Search frame
        search_frame = ttk.LabelFrame(parent, text="Rechercher des élèves", padding="8")
        search_frame.pack(fill="x", pady=(0, 8))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", padx=(0, 8))
        
        ttk.Button(search_frame, text="Rechercher", command=self._search_students).pack(side="left", padx=(0, 8))
        ttk.Button(search_frame, text="Tous les élèves", command=self._show_all_students).pack(side="left")
        
        # Results frame
        results_frame = ttk.LabelFrame(parent, text="Résultats de recherche", padding="8")
        results_frame.pack(fill="both", expand=True)
        
        # Results treeview
        columns = ("id", "enrollment_no", "name")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=12)
        
        self.results_tree.heading("id", text="ID")
        self.results_tree.heading("enrollment_no", text="Matricule")
        self.results_tree.heading("name", text="Nom")
        
        self.results_tree.column("id", width=60)
        self.results_tree.column("enrollment_no", width=120)
        self.results_tree.column("name", width=200)
        
        # Scrollbar
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
        
        # Actions frame
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill="x", pady=(8, 0))
        
        ttk.Button(actions_frame, text="Inscrire Sélectionné", 
                  command=self._enroll_selected, style="Primary.TButton").pack(side="left")
        ttk.Button(actions_frame, text="Inscrire Tous", 
                  command=self._enroll_all).pack(side="left", padx=(8, 0))
        
        # Bind double-click to enroll
        self.results_tree.bind("<Double-1>", lambda e: self._enroll_selected())

    def _load_enrolled_students(self):
        """Load enrolled students for the current class"""
        # Clear existing items
        for item in self.enrolled_tree.get_children():
            self.enrolled_tree.delete(item)
        
        try:
            enrolled_students = list_enrolled_students(self.class_id)
            for student in enrolled_students:
                name = f"{student['last_name']} {student['first_name']}"
                self.enrolled_tree.insert("", "end", iid=student["id"], 
                                        values=(student["id"], student["enrollment_no"], name, ""))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les élèves inscrits: {str(e)}")

    def _search_students(self):
        """Search for students"""
        query = self.search_var.get().strip()
        self._populate_results(query)

    def _show_all_students(self):
        """Show all students"""
        self._populate_results("")

    def _populate_results(self, query: str):
        """Populate the results treeview with students"""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        try:
            students = list_students(query=query)
            for student in students:
                name = f"{student['last_name']} {student['first_name']}"
                self.results_tree.insert("", "end", iid=student["id"], 
                                       values=(student["id"], student["enrollment_no"], name))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche: {str(e)}")

    def _enroll_selected(self):
        """Enroll selected students"""
        selected_items = self.results_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Veuillez sélectionner au moins un élève.")
            return
        
        success_count = 0
        for item_id in selected_items:
            student_id = int(item_id)
            try:
                enroll_student(self.class_id, student_id)
                success_count += 1
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'inscription de l'élève {student_id}: {str(e)}")
        
        if success_count > 0:
            messagebox.showinfo("Succès", f"{success_count} élève(s) inscrit(s) avec succès.")
            self._load_enrolled_students()
            if self.on_enrollment_changed:
                self.on_enrollment_changed()

    def _enroll_all(self):
        """Enroll all students in the results"""
        all_items = self.results_tree.get_children()
        if not all_items:
            messagebox.showinfo("Info", "Aucun élève à inscrire.")
            return
        
        success_count = 0
        for item_id in all_items:
            student_id = int(item_id)
            try:
                enroll_student(self.class_id, student_id)
                success_count += 1
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'inscription de l'élève {student_id}: {str(e)}")
        
        if success_count > 0:
            messagebox.showinfo("Succès", f"{success_count} élève(s) inscrit(s) avec succès.")
            self._load_enrolled_students()
            if self.on_enrollment_changed:
                self.on_enrollment_changed()

    def _unenroll_selected(self):
        """Unenroll selected students"""
        selected_items = self.enrolled_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Veuillez sélectionner au moins un élève à désinscrire.")
            return
        
        if not messagebox.askyesno("Confirmation", 
                                 f"Confirmez-vous la désinscription de {len(selected_items)} élève(s) ?"):
            return
        
        success_count = 0
        for item_id in selected_items:
            student_id = int(item_id)
            try:
                unenroll_student(self.class_id, student_id)
                success_count += 1
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la désinscription de l'élève {student_id}: {str(e)}")
        
        if success_count > 0:
            messagebox.showinfo("Succès", f"{success_count} élève(s) désinscrit(s) avec succès.")
            self._load_enrolled_students()
            if self.on_enrollment_changed:
                self.on_enrollment_changed()

