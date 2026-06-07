import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from services.class_service import list_classes, list_enrolled_students
from services.attendance_service import get_or_create_session, list_sessions, list_attendance, upsert_attendance, ensure_records_for_enrolled
from services.fees_service import generate_invoices_for_session

STATUS_OPTIONS = ["Present", "Absent", "Late", "Excused"]


class AttendanceView(ttk.Frame):
    def __init__(self, master, current_user_id: int = None):
        super().__init__(master)
        self.class_id = None
        self.session_id = None
        self.current_user_id = current_user_id
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        # Left: select class and date
        left = ttk.Frame(self, style="Card.TFrame", padding=16)
        left.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        left.columnconfigure(1, weight=1)
        ttk.Label(left, text="Présences", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(left, text="Classe").grid(row=1, column=0, sticky="w", pady=(8,2))
        self.class_combo = ttk.Combobox(left, state="readonly")
        self.class_combo.grid(row=1, column=1, sticky="ew")
        self._load_classes()
        ttk.Button(left, text="Actualiser classes", command=self._load_classes).grid(row=1, column=2, padx=6)

        ttk.Label(left, text="Date").grid(row=2, column=0, sticky="w", pady=(8,2))
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(left, textvariable=self.date_var).grid(row=2, column=1, sticky="ew")

        ttk.Button(left, text="Ouvrir séance", style="Primary.TButton", command=self._open_session).grid(row=3, column=0, columnspan=3, pady=(12,0), sticky="ew")

        # Right: attendance table
        right = ttk.Frame(self, style="Card.TFrame", padding=16)
        right.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        right.columnconfigure(0, weight=1)
        ttk.Label(right, text="État de présence", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        cols = ("enrollment_no", "name", "status", "note")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=16, style="Modern.Treeview")
        self.tree.heading("enrollment_no", text="Matricule", anchor="w")
        self.tree.heading("name", text="Nom", anchor="w")
        self.tree.heading("status", text="Statut", anchor="w")
        self.tree.heading("note", text="Note", anchor="w")
        for c in cols:
            self.tree.column(c, anchor="w", width=140)
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(8,8))
        right.rowconfigure(1, weight=1)

        actions = ttk.Frame(right)
        actions.grid(row=2, column=0, sticky="e")
        ttk.Button(actions, text="Présent", command=lambda: self._set_status("Present")).grid(row=0, column=0, padx=4)
        ttk.Button(actions, text="Absent", command=lambda: self._set_status("Absent")).grid(row=0, column=1, padx=4)
        ttk.Button(actions, text="Retard", command=lambda: self._set_status("Late")).grid(row=0, column=2, padx=4)
        ttk.Button(actions, text="Justifié", command=lambda: self._set_status("Excused")).grid(row=0, column=3, padx=4)

    def _load_classes(self):
        items = list_classes()
        display = [f"{c['name']} ({c.get('academic_year') or ''})" for c in items]
        self.class_combo["values"] = display
        self._classes = items
        if items:
            self.class_combo.current(0)

    def _open_session(self):
        if not self._classes:
            messagebox.showinfo("Info", "Aucune classe disponible.")
            return
        idx = self.class_combo.current()
        if idx < 0:
            messagebox.showinfo("Info", "Sélectionnez une classe.")
            return
        self.class_id = self._classes[idx]["id"]
        session_date = self.date_var.get().strip()
        try:
            self.session_id = get_or_create_session(self.class_id, session_date, user_id=self.current_user_id)
            # Auto-generate invoices for this session based on fee rules
            try:
                generate_invoices_for_session(self.class_id, self.session_id)
            except Exception:
                # Non-blocking if fee rules missing or any issue; attendance continues
                pass
            self._load_attendance()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _load_attendance(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if not self.class_id or not self.session_id:
            return
        # Ensure records exist for enrolled students (non-destructive)
        ensure_records_for_enrolled(self.session_id, self.class_id, default_status="Present")
        for r in list_attendance(self.session_id):
            name = f"{r['last_name']} {r['first_name']}"
            self.tree.insert("", "end", iid=r["student_id"], values=(r["enrollment_no"], name, r["status"], r["note"] or ""))

    def _selected_student_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _set_status(self, status: str):
        if not self.session_id:
            messagebox.showinfo("Info", "Ouvrez une séance d'abord.")
            return
        sid = self._selected_student_id()
        if not sid:
            messagebox.showinfo("Info", "Sélectionnez un élève.")
            return
        try:
            upsert_attendance(self.session_id, sid, status, user_id=self.current_user_id)
            self._load_attendance()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))