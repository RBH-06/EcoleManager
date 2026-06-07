import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
import calendar
from datetime import date as dt_date
import csv
import tempfile
import os
import subprocess

from services.student_service import list_students, create_student, update_student, delete_student, get_student
from services.class_service import list_classes


class StudentForm(ttk.Frame):
    def __init__(self, master, on_saved, current_user_id: Optional[int] = None):
        super().__init__(master, style="Card.TFrame", padding=16)
        self.on_saved = on_saved
        self.current_user_id = current_user_id
        self.student_id: Optional[int] = None
        self._build()

    def _build(self):
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Fiche Élève", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,8))

        labels = [
            ("Prénom", "first_name"),
            ("Nom", "last_name"),
            ("Date de naissance", "date_of_birth"),
            ("Sexe", "gender"),
            ("Adresse", "address"),
            ("Téléphone (Élève)", "student_phone"),
            ("Téléphone Parent", "phone"),
            ("Email", "email"),
        ]
        self.vars = {}
        r = 1
        for label, key in labels:
            ttk.Label(self, text=label).grid(row=r, column=0, sticky="w", pady=4)
            var = tk.StringVar()
            self.vars[key] = var
            if key == "date_of_birth":
                # date picker: 3 combo boxes (year, month, day)
                dob_frame = ttk.Frame(self)
                dob_frame.grid(row=r, column=1, sticky="ew", pady=4)
                dob_frame.columnconfigure(2, weight=1)

                # Year combobox (e.g., 1990..current year)
                current_year = dt_date.today().year
                years = [str(y) for y in range(current_year - 30, current_year + 1)]
                self._dob_year = ttk.Combobox(dob_frame, state="readonly", values=years, width=6)
                self._dob_year.grid(row=0, column=0)

                # Month combobox 1..12 with names
                months = [f"{i:02d} - {calendar.month_name[i]}" for i in range(1, 12 + 1)]
                self._dob_month = ttk.Combobox(dob_frame, state="readonly", values=months, width=14)
                self._dob_month.grid(row=0, column=1, padx=4)

                # Day combobox depends on month/year
                self._dob_day = ttk.Combobox(dob_frame, state="readonly", width=4)
                self._dob_day.grid(row=0, column=2)

                def _update_days(*_):
                    try:
                        y = int(self._dob_year.get() or 0)
                        m = int((self._dob_month.get() or "01").split(" ")[0])
                        last_day = calendar.monthrange(y, m)[1]
                        self._dob_day["values"] = [f"{d:02d}" for d in range(1, last_day + 1)]
                        if int(self._dob_day.get() or 0) > last_day:
                            self._dob_day.set("")
                    except Exception:
                        self._dob_day["values"] = [f"{d:02d}" for d in range(1, 31)]

                self._dob_year.bind("<<ComboboxSelected>>", _update_days)
                self._dob_month.bind("<<ComboboxSelected>>", _update_days)

                # initialize defaults
                self._dob_year.current(len(years) - 10 if len(years) >= 10 else 0)
                self._dob_month.current(0)
                _update_days()

                # keep original text var in sync on save
            else:
                # gender as dropdown M/F
                if key == "gender":
                    entry = ttk.Combobox(self, state="readonly", values=["M", "F"], textvariable=var)
                else:
                    entry = ttk.Entry(self, textvariable=var)
                entry.grid(row=r, column=1, sticky="ew", pady=4)
            r += 1

        btns = ttk.Frame(self)
        btns.grid(row=r, column=0, columnspan=2, sticky="e", pady=(8,0))
        ttk.Button(btns, text="Annuler", command=self._reset).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Enregistrer", style="Primary.TButton", command=self._save).grid(row=0, column=1)

    def load_student(self, student_id: int):
        self.student_id = student_id
        data = get_student(student_id)
        if not data:
            messagebox.showerror("Erreur", "Élève introuvable.")
            return
        for k, v in self.vars.items():
            v.set(data.get(k, "") or "")
        # sync DOB combos if date exists
        dob = data.get("date_of_birth") or ""
        if dob and hasattr(self, "_dob_year"):
            try:
                y, m, d = dob.split("-")
                values_years = list(self._dob_year["values"]) or []
                if y in values_years:
                    self._dob_year.set(y)
                else:
                    self._dob_year.set(values_years[-1] if values_years else "")
                # month values like "01 - January"
                m_idx = int(m)
                month_label = f"{int(m):02d} - {calendar.month_name[m_idx]}"
                self._dob_month.set(month_label)
                # update days then set day
                def _set_day():
                    last_day = calendar.monthrange(int(self._dob_year.get() or 0), int(m))[1]
                    self._dob_day["values"] = [f"{d:02d}" for d in range(1, last_day + 1)]
                    self._dob_day.set(d)
                _set_day()
            except Exception:
                pass

    def _reset(self):
        self.student_id = None
        for v in self.vars.values():
            v.set("")

    def _save(self):
        # assemble date from combos
        if hasattr(self, "_dob_year"):
            y = self._dob_year.get()
            m = (self._dob_month.get() or "01").split(" ")[0]
            d = self._dob_day.get()
            self.vars["date_of_birth"].set(f"{y}-{m}-{d}" if y and m and d else "")
        data = {k: v.get().strip() for k, v in self.vars.items()}

        # validations
        if not data["first_name"] or not data["last_name"]:
            messagebox.showwarning("Champs requis", "Prénom et Nom sont obligatoires.")
            return
        if not data.get("student_phone"):
            messagebox.showwarning("Champs requis", "Téléphone de l'élève est obligatoire.")
            return
        if not data.get("phone"):
            messagebox.showwarning("Champs requis", "Téléphone Parent est obligatoire.")
            return
        if data.get("gender") not in ("M", "F"):
            messagebox.showwarning("Champ requis", "Veuillez sélectionner le sexe: M ou F.")
            return
        # optional: validate date format when provided
        if data.get("date_of_birth") and len(data["date_of_birth"]) != 10:
            messagebox.showwarning("Date invalide", "Veuillez sélectionner une date de naissance valide.")
            return
        try:
            if self.student_id:
                data["_actor_user_id"] = self.current_user_id
                update_student(self.student_id, data)
            else:
                data["_actor_user_id"] = self.current_user_id
                self.student_id = create_student(data)
            messagebox.showinfo("Succès", "Enregistré avec succès.")
            self.on_saved()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


class StudentsList(ttk.Frame):
    def __init__(self, master, on_select, current_user_id: Optional[int] = None):
        super().__init__(master, style="Card.TFrame", padding=16)
        self.on_select = on_select
        self.current_user_id = current_user_id
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        ttk.Label(self, text="Liste des Élèves", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        # Search bar with filters
        search_frame = ttk.Frame(self)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(8,8))
        search_frame.columnconfigure(1, weight=2)
        search_frame.columnconfigure(3, weight=1)

        ttk.Label(search_frame, text="Recherche").grid(row=0, column=0, sticky="w")
        self.query_var = tk.StringVar()
        query_entry = ttk.Entry(search_frame, textvariable=self.query_var)
        query_entry.grid(row=0, column=1, sticky="ew", padx=8)
        query_entry.bind("<Return>", lambda e: self._reload())

        ttk.Label(search_frame, text="Classe").grid(row=0, column=2, sticky="w")
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(search_frame, state="readonly")
        self.class_combo.grid(row=0, column=3, sticky="ew", padx=8)
        self.class_combo.bind("<<ComboboxSelected>>", lambda e: self._reload())

        ttk.Label(search_frame, text="Sexe").grid(row=0, column=4, sticky="w")
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(search_frame, state="readonly", values=["", "M", "F", "Autre"])
        self.gender_combo.grid(row=0, column=5, sticky="ew", padx=8)
        self.gender_combo.bind("<<ComboboxSelected>>", lambda e: self._reload())

        ttk.Button(search_frame, text="Réinitialiser", command=self._reset_filters).grid(row=0, column=6, padx=4)
        ttk.Button(search_frame, text="Rechercher", style="Primary.TButton", command=self._reload).grid(row=0, column=7)

        # populate classes
        self._load_classes_filter()

        # Treeview with multiple selection
        cols = ("id", "enrollment_no", "last_name", "first_name", "date_of_birth", "gender", "phone")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12, style="Modern.Treeview", selectmode="extended")
        headings = {
            "id": "ID",
            "enrollment_no": "Matricule",
            "last_name": "Nom",
            "first_name": "Prénom",
            "date_of_birth": "Naissance",
            "gender": "Sexe",
            "phone": "Téléphone",
        }
        for c in cols:
            self.tree.heading(c, text=headings[c], anchor="w")
            self.tree.column(c, stretch=True, width=120, anchor="w")
        self.tree.grid(row=2, column=0, sticky="nsew")
        self.rowconfigure(2, weight=1)

        # Actions
        actions = ttk.Frame(self)
        actions.grid(row=3, column=0, sticky="e", pady=(8,0))
        ttk.Button(actions, text="Nouveau", style="Primary.TButton", command=self._new).grid(row=0, column=0, padx=4)
        ttk.Button(actions, text="Modifier", command=self._edit).grid(row=0, column=1, padx=4)
        ttk.Button(actions, text="Supprimer", command=self._delete).grid(row=0, column=2, padx=4)
        ttk.Button(actions, text="Exporter CSV", command=self._export_csv).grid(row=0, column=3, padx=4)
        ttk.Button(actions, text="Imprimer", command=self._print_list).grid(row=0, column=4)

        self._reload()

    def _load_classes_filter(self):
        items = list_classes()
        display = [f"{c['name']} ({c.get('academic_year') or ''})" for c in items]
        self.class_combo["values"] = [""] + display
        self._classes = items
        # Default to no class filter
        self.class_combo.current(0)

    def _reset_filters(self):
        self.query_var.set("")
        if hasattr(self, "class_combo"):
            self.class_combo.current(0)
        if hasattr(self, "gender_combo"):
            self.gender_combo.set("")
        # Just reload existing tree
        if hasattr(self, "tree"):
            self._reload()

    def _reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = self.query_var.get().strip()
        # class filter: map display index (0 is empty) to class id
        class_id = None
        if hasattr(self, "_classes") and self.class_combo.get():
            idx = self.class_combo.current()
            if idx > 0:  # 0 = no class filter
                real_idx = idx - 1
                if 0 <= real_idx < len(self._classes):
                    class_id = self._classes[real_idx]["id"]
        gender = self.gender_combo.get().strip() or None

        for row in list_students(query=query, gender=gender, class_id=class_id):
            self.tree.insert("", "end", iid=row["id"], values=(
                row["id"], row["enrollment_no"], row["last_name"], row["first_name"], row["date_of_birth"] or "", row["gender"] or "", row["phone"] or "",
            ))

    def _selected_ids(self) -> list:
        return [int(sel) for sel in self.tree.selection()]

    def _selected_id(self) -> Optional[int]:
        sel = self.tree.selection()
        if not sel:
            return None
        return int(sel[0])

    def _export_csv(self):
        # Gather current rows
        rows = []
        for iid in self.tree.get_children():
            rows.append(self.tree.item(iid)["values"])
        if not rows:
            messagebox.showinfo("Export CSV", "Aucune donnée à exporter.")
            return
        path = filedialog.asksaveasfilename(
            title="Exporter CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="students.csv",
        )
        if not path:
            return
        headers = ["ID", "Matricule", "Nom", "Prénom", "Naissance", "Sexe", "Téléphone"]
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for r in rows:
                    writer.writerow(r)
            messagebox.showinfo("Export CSV", f"Exporté vers {path}")
        except Exception as e:
            messagebox.showerror("Export CSV", str(e))

    def _print_list(self):
        # Directly open the print dialog for the student list
        try:
            tmpdir = tempfile.gettempdir()
            tmpfile = os.path.join(tmpdir, "students_print.csv")
            headers = ["ID", "Matricule", "Nom", "Prénom", "Naissance", "Sexe", "Téléphone"]
            with open(tmpfile, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for iid in self.tree.get_children():
                    writer.writerow(self.tree.item(iid)["values"])

            # Use system-specific command to open the print dialog
            if os.name == "nt":  # Windows
                os.startfile(tmpfile, "print")
            else:
                subprocess.Popen(["lp", tmpfile])
        except Exception as e:
            messagebox.showerror("Imprimer", str(e))

    def _new(self):
        self.on_select(None)

    def _edit(self):
        sid = self._selected_id()
        if sid is None:
            messagebox.showinfo("Info", "Sélectionnez un élève à modifier.")
            return
        self.on_select(sid)

    def _delete(self):
        sids = self._selected_ids()
        if not sids:
            messagebox.showinfo("Info", "Sélectionnez un ou plusieurs élèves à supprimer.")
            return
        warning = (
            "Supprimer ces élèves va également supprimer leurs inscriptions, présences, et factures associées.\n"
            "Toute facture impayée sera perdue. Confirmez-vous la suppression ?"
        )
        if not messagebox.askyesno("Confirmation", warning):
            return
        try:
            for sid in sids:
                delete_student(sid, actor_user_id=self.current_user_id)
            self._reload()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


class StudentsView(ttk.Frame):
    def __init__(self, master, current_user_id: Optional[int] = None):
        super().__init__(master)
        self.current_user_id = current_user_id
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)

        self.list_panel = StudentsList(self, on_select=self._on_select, current_user_id=self.current_user_id)
        self.list_panel.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        self.form_panel = StudentForm(self, on_saved=self._on_saved, current_user_id=self.current_user_id)
        self.form_panel.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)

    def _on_select(self, student_id: Optional[int]):
        if student_id:
            self.form_panel.load_student(student_id)
        else:
            self.form_panel._reset()

    def _on_saved(self):
        self.list_panel._reload()