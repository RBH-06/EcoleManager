import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from services.class_service import list_classes
from services.fees_service import set_fee_rule, get_fee_rule, list_invoices_for_session, mark_invoice_paid, mark_invoice_unpaid, list_invoices_with_attendance, generate_invoices_for_session, list_unpaid_invoices_by_class
from services.attendance_service import list_sessions


class FeesView(ttk.Frame):
    """Simple fees management UI:
    - Configure per-session fee for a class
    - List sessions and their invoices
    - Mark selected invoice as paid/unpaid
    """

    def __init__(self, master, current_user_id: int = None):
        super().__init__(master)
        self.class_id: Optional[int] = None
        self.session_id: Optional[int] = None
        self.current_user_id = current_user_id
        self._build()

    def _build(self):
        # Configure main grid
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        # Left panel: class and rule config
        left = ttk.Frame(self, style="Card.TFrame", padding=16)
        left.grid(row=0, column=0, sticky="nsew", padx=(16,8), pady=16)
        left.columnconfigure(1, weight=1)
        
        ttk.Label(left, text="Configuration des frais", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,16))

        ttk.Label(left, text="Classe:").grid(row=1, column=0, sticky="w", pady=(0,8))
        self.class_combo = ttk.Combobox(left, state="readonly", width=25)
        self.class_combo.grid(row=1, column=1, sticky="ew", pady=(0,8))
        ttk.Button(left, text="🔄", command=self._load_classes).grid(row=1, column=2, padx=(8,0), pady=(0,8))

        ttk.Label(left, text="Montant (MAD):").grid(row=2, column=0, sticky="w", pady=(0,8))
        self.amount_var = tk.StringVar(value="0")
        ttk.Entry(left, textvariable=self.amount_var, width=20).grid(row=2, column=1, sticky="ew", pady=(0,8))
        
        ttk.Button(left, text="💾 Enregistrer règle", style="Primary.TButton", command=self._save_rule).grid(row=3, column=0, columnspan=3, sticky="ew", pady=(16,0))

        # Right panel: sessions and payments
        right = ttk.Frame(self, style="Card.TFrame", padding=16)
        right.grid(row=0, column=1, sticky="nsew", padx=(8,16), pady=16)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)  # Sessions area
        right.rowconfigure(3, weight=2)  # Students area (bigger)
        
        # Header
        header_frame = ttk.Frame(right)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0,12))
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=0)
        
        ttk.Label(header_frame, text="💰 Gestion des Paiements", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        info_text = "Sélectionnez une classe, puis une séance pour gérer les paiements"
        ttk.Label(header_frame, text=info_text, font=("Arial", 9), foreground="gray").grid(row=1, column=0, sticky="w")
        
        # Button to view all unpaid students in the selected class
        ttk.Button(header_frame, text="🔎 Voir impayés (classe)", command=self._show_unpaid_popup).grid(row=0, column=1, rowspan=2, sticky="e")

        # Sessions section
        sessions_frame = ttk.LabelFrame(right, text="📅 Sessions", padding="8")
        sessions_frame.grid(row=1, column=0, sticky="nsew", pady=(0,12))
        sessions_frame.columnconfigure(0, weight=1)
        sessions_frame.rowconfigure(0, weight=1)
        
        # Sessions treeview with scrollbar
        sessions_container = ttk.Frame(sessions_frame)
        sessions_container.grid(row=0, column=0, sticky="nsew")
        sessions_container.columnconfigure(0, weight=1)
        sessions_container.rowconfigure(0, weight=1)
        
        self.sessions = ttk.Treeview(sessions_container, columns=("id", "date"), show="headings", height=4)
        self.sessions.heading("id", text="ID", anchor="w")
        self.sessions.heading("date", text="Date de séance", anchor="w")
        self.sessions.column("id", width=60, anchor="w")
        self.sessions.column("date", width=200, anchor="w")
        
        sessions_scrollbar = ttk.Scrollbar(sessions_container, orient="vertical", command=self.sessions.yview)
        self.sessions.configure(yscrollcommand=sessions_scrollbar.set)
        
        self.sessions.grid(row=0, column=0, sticky="nsew")
        sessions_scrollbar.grid(row=0, column=1, sticky="ns")
        self.sessions.bind("<<TreeviewSelect>>", lambda e: self._load_invoices())

        # Students section with legend
        students_frame = ttk.LabelFrame(right, text="👥 Élèves et Paiements", padding="8")
        students_frame.grid(row=3, column=0, sticky="nsew")
        students_frame.columnconfigure(0, weight=1)
        students_frame.rowconfigure(1, weight=1)
        
        # Legend at top of students section
        legend_frame = ttk.Frame(students_frame)
        legend_frame.grid(row=0, column=0, sticky="ew", pady=(0,8))
        legend_text = "🟢 Présent  🔴 Absent (paiement bloqué)  🟡 Retard  🔵 Justifié"
        ttk.Label(legend_frame, text=legend_text, font=("Arial", 8)).pack()

        # Students treeview with scrollbar
        students_container = ttk.Frame(students_frame)
        students_container.grid(row=1, column=0, sticky="nsew")
        students_container.columnconfigure(0, weight=1)
        students_container.rowconfigure(0, weight=1)

        # invoices table with attendance status
        cols = ("id", "enrollment_no", "name", "attendance", "amount", "payment_status", "attendance_raw")
        self.invoices = ttk.Treeview(students_container, columns=cols, show="headings")
        headers = {
            "id": "ID",
            "enrollment_no": "Matricule", 
            "name": "Nom",
            "attendance": "Présence",
            "amount": "Montant",
            "payment_status": "Paiement",
        }
        
        for c in cols:
            if c != "attendance_raw":  # Don't show heading for hidden column
                self.invoices.heading(c, text=headers.get(c, ""), anchor="w")
            
            if c == "id":
                self.invoices.column(c, width=50, anchor="w")
            elif c == "enrollment_no":
                self.invoices.column(c, width=80, anchor="w")
            elif c == "name":
                self.invoices.column(c, width=150, anchor="w")
            elif c == "attendance":
                self.invoices.column(c, width=80, anchor="center")
            elif c == "amount":
                self.invoices.column(c, width=80, anchor="w")
            elif c == "payment_status":
                self.invoices.column(c, width=100, anchor="w")
            elif c == "attendance_raw":
                self.invoices.column(c, width=0, minwidth=0)  # Hidden column

        invoices_scrollbar = ttk.Scrollbar(students_container, orient="vertical", command=self.invoices.yview)
        self.invoices.configure(yscrollcommand=invoices_scrollbar.set)
        
        self.invoices.grid(row=0, column=0, sticky="nsew")
        invoices_scrollbar.grid(row=0, column=1, sticky="ns")

        # Action buttons
        actions_frame = ttk.Frame(students_frame)
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(12,0))
        
        ttk.Button(actions_frame, text="✅ Marquer Payé", command=self._mark_paid).pack(side="left", padx=(0,8))
        ttk.Button(actions_frame, text="❌ Marquer Impayé", command=self._mark_unpaid).pack(side="left")

        # initialize
        self._load_classes()

    def _load_classes(self):
        items = list_classes()
        display = [f"{c['name']} ({c.get('academic_year') or ''})" for c in items]
        self.class_combo["values"] = display
        self._classes = items
        if items:
            self.class_combo.current(0)
            self._on_class_changed()
        self.class_combo.bind("<<ComboboxSelected>>", lambda e: self._on_class_changed())

    def _on_class_changed(self):
        idx = self.class_combo.current()
        if idx < 0:
            return
        self.class_id = self._classes[idx]["id"]
        # load rule
        rule = get_fee_rule(self.class_id)
        self.amount_var.set(str((rule["amount_cents"] if rule else 0) / 100))
        # load sessions
        self._load_sessions()

    def _save_rule(self):
        if not self.class_id:
            messagebox.showinfo("Info", "Sélectionnez une classe.")
            return
        try:
            amount_mad = float(self.amount_var.get().strip() or 0)
            if amount_mad < 0:
                raise ValueError("Montant invalide")
            set_fee_rule(self.class_id, int(round(amount_mad * 100)))
            messagebox.showinfo("Succès", "Règle enregistrée.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _load_sessions(self):
        for i in self.sessions.get_children():
            self.sessions.delete(i)
        self.session_id = None
        if not self.class_id:
            return
        
        # Load sessions and ensure invoices exist for them
        sessions = list_sessions(self.class_id, limit=100)
        for row in sessions:
            self.sessions.insert("", "end", iid=row["id"], values=(row["id"], row["session_date"]))
            
            # Auto-generate missing invoices for existing sessions
            try:
                generate_invoices_for_session(self.class_id, row["id"])
            except Exception:
                # Silently ignore errors (e.g., no fee rule set up yet)
                pass

    def _load_invoices(self):
        for i in self.invoices.get_children():
            self.invoices.delete(i)
        sel = self.sessions.selection()
        if not sel:
            return
        self.session_id = int(sel[0])
        
        try:
            # Try to generate invoices if they don't exist
            generate_invoices_for_session(self.class_id, self.session_id)
        except Exception:
            pass
        
        # Configure tags for color coding
        self.invoices.tag_configure("absent", background="#ffcccc", foreground="#cc0000")  # Light red background, red text
        self.invoices.tag_configure("present", background="#ccffcc")  # Light green background
        self.invoices.tag_configure("late", background="#fff3cd")  # Light yellow background
        self.invoices.tag_configure("excused", background="#cce5ff")  # Light blue background
        
        try:
            invoices = list_invoices_with_attendance(self.session_id)
            if not invoices:
                # Insert a message row if no invoices found
                self.invoices.insert("", "end", values=("", "", "Aucune facture trouvée. Vérifiez que la règle de frais est définie pour cette classe.", "", "", "", ""))
                return
                
            for inv in invoices:
                name = f"{inv['last_name']} {inv['first_name']}"
                amount = f"{inv['amount_cents']/100:.2f} {inv['currency']}"
                attendance_status = inv['attendance_status']
                
                # Translate attendance status to French
                attendance_display = {
                    "Present": "Présent",
                    "Absent": "Absent",
                    "Late": "Retard",
                    "Excused": "Justifié",
                    "Unknown": "Inconnu"
                }.get(attendance_status, attendance_status)
                
                # Determine tag for color coding
                tag = ""
                if attendance_status == "Absent":
                    tag = "absent"
                elif attendance_status == "Present":
                    tag = "present"
                elif attendance_status == "Late":
                    tag = "late"
                elif attendance_status == "Excused":
                    tag = "excused"
                
                item_id = self.invoices.insert("", "end", 
                                             iid=inv["id"], 
                                             values=(inv["id"], inv["enrollment_no"], name, 
                                                   attendance_display, amount, inv["payment_status"], attendance_status),
                                             tags=(tag,) if tag else ())
        except Exception as e:
            # Show error message in the table
            self.invoices.insert("", "end", values=("", "", f"Erreur lors du chargement: {str(e)}", "", "", "", ""))

    def _selected_invoice_id(self) -> Optional[int]:
        sel = self.invoices.selection()
        return int(sel[0]) if sel else None
    
    def _get_selected_attendance_status(self) -> Optional[str]:
        """Get the attendance status of the selected invoice"""
        sel = self.invoices.selection()
        if not sel:
            return None
        item_id = sel[0]
        return self.invoices.set(item_id, "attendance_raw")
    
    def _validate_payment_eligibility(self) -> bool:
        """Check if selected student is eligible for payment (must be present)"""
        attendance_status = self._get_selected_attendance_status()
        if attendance_status in ["Absent"]:
            messagebox.showwarning(
                "Paiement non autorisé", 
                "Impossible de marquer comme payé : l'élève était absent.\n\n"
                "Seuls les élèves présents peuvent effectuer des paiements."
            )
            return False
        elif attendance_status == "Unknown":
            result = messagebox.askyesno(
                "Statut de présence inconnu",
                "Le statut de présence de cet élève n'est pas enregistré.\n\n"
                "Voulez-vous continuer avec le paiement ?"
            )
            return result
        return True

    def _mark_paid(self):
        iid = self._selected_invoice_id()
        if not iid:
            messagebox.showinfo("Info", "Sélectionnez une facture.")
            return
        
        # Check attendance eligibility
        if not self._validate_payment_eligibility():
            return
        
        try:
            mark_invoice_paid(iid, user_id=self.current_user_id)
            self._load_invoices()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _mark_unpaid(self):
        iid = self._selected_invoice_id()
        if not iid:
            messagebox.showinfo("Info", "Sélectionnez une facture.")
            return
        try:
            mark_invoice_unpaid(iid, user_id=self.current_user_id)
            self._load_invoices()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # --- Popup: Show all unpaid students for the selected class ---
    def _show_unpaid_popup(self):
        if not self.class_id:
            messagebox.showinfo("Info", "Sélectionnez une classe d'abord.")
            return

        # Ensure invoices exist for all sessions of this class (best effort)
        try:
            sessions = list_sessions(self.class_id, limit=1000)
            for s in sessions:
                try:
                    generate_invoices_for_session(self.class_id, s["id"])
                except Exception:
                    pass
        except Exception:
            pass

        # Fetch unpaid invoices
        try:
            data = list_unpaid_invoices_by_class(self.class_id)
        except Exception as e:
            messagebox.showerror("Erreur", f"Chargement des impayés a échoué:\n{e}")
            return

        # Build popup window
        win = tk.Toplevel(self)
        win.title("Élèves impayés (classe)")
        win.geometry("720x420")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        container = ttk.Frame(win, padding=12)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        # Header with count
        count = len(data)
        ttk.Label(container, text=f"Impayés: {count}", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0,8))

        # Table
        cols = ("enrollment_no", "name", "session_date", "amount", "status")
        tree = ttk.Treeview(container, columns=cols, show="headings")
        tree.heading("enrollment_no", text="Matricule", anchor="w")
        tree.heading("name", text="Nom", anchor="w")
        tree.heading("session_date", text="Date séance", anchor="w")
        tree.heading("amount", text="Montant", anchor="center")
        tree.heading("status", text="Statut", anchor="w")

        tree.column("enrollment_no", width=100, anchor="w")
        tree.column("name", width=200, anchor="w")
        tree.column("session_date", width=120, anchor="w")
        tree.column("amount", width=100, anchor="center")
        tree.column("status", width=100, anchor="w")

        # Tag styles
        tree.tag_configure("absent", background="#ffcccc", foreground="#cc0000")

        vs = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vs.set)

        tree.grid(row=1, column=0, sticky="nsew")
        vs.grid(row=1, column=1, sticky="ns")

        # Fill rows
        for row in data:
            name = f"{row['last_name']} {row['first_name']}"
            amount = f"{row['amount_cents']/100:.2f} {row['currency']}"
            # Build status text with reason if absent
            status_text = row["payment_status"]
            if row.get("attendance_status") == "Absent":
                status_text = f"Impayé (Absent)"
                tags = ("absent",)
            else:
                tags = ()
            tree.insert(
                "",
                "end",
                values=(row["enrollment_no"], name, row["session_date"], amount, status_text),
                tags=tags
            )

        # Footer actions (Close only)
        footer = ttk.Frame(container)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8,0))
        footer.columnconfigure(0, weight=1)
        ttk.Button(footer, text="Fermer", command=win.destroy).pack(side="right")