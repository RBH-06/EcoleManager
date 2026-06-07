import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from datetime import date, datetime

from services.class_service import list_enrolled_students
from services.attendance_service import (
    get_or_create_session, 
    list_sessions, 
    list_attendance, 
    upsert_attendance, 
    ensure_records_for_enrolled,
    delete_session,
    get_session_info
)
from services.fees_service import generate_invoices_for_session


class AttendanceDialog(tk.Toplevel):
    def __init__(self, parent, class_id: int, class_name: str, on_attendance_changed: Optional[Callable] = None):
        super().__init__(parent)
        self.class_id = class_id
        self.class_name = class_name
        self.on_attendance_changed = on_attendance_changed
        self.current_session_id = None
        
        # Configure dialog
        self.title(f"Présences - {class_name}")
        self.geometry("900x700")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.center_window()
        
        self._build()
        self._load_sessions()

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
        title_label = ttk.Label(main_frame, text=f"Gestion des Présences - {self.class_name}", 
                               font=("Arial", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 16))
        
        # Top section - Session selection and creation
        top_frame = ttk.LabelFrame(main_frame, text="Sélection de Session", padding="12")
        top_frame.pack(fill="x", pady=(0, 16))
        
        # Session selection
        session_frame = ttk.Frame(top_frame)
        session_frame.pack(fill="x", pady=(0, 8))
        
        ttk.Label(session_frame, text="Sessions existantes:").pack(side="left")
        self.session_var = tk.StringVar()
        self.session_combo = ttk.Combobox(session_frame, textvariable=self.session_var, width=30, state="readonly")
        self.session_combo.pack(side="left", padx=(8, 16))
        self.session_combo.bind("<<ComboboxSelected>>", self._on_session_selected)
        
        ttk.Button(session_frame, text="Actualiser Sessions", 
                  command=self._load_sessions).pack(side="left", padx=(0, 8))
        # Delete button with warning color (if supported by theme)
        delete_btn = ttk.Button(session_frame, text="🗑 Supprimer Session", 
                               command=self._delete_selected_session)
        delete_btn.pack(side="left", padx=(8, 0))
        
        # New session creation
        new_session_frame = ttk.Frame(top_frame)
        new_session_frame.pack(fill="x")
        
        ttk.Label(new_session_frame, text="Nouvelle session:").pack(side="left")
        self.new_session_date_var = tk.StringVar(value=date.today().isoformat())
        date_entry = ttk.Entry(new_session_frame, textvariable=self.new_session_date_var, width=15)
        date_entry.pack(side="left", padx=(8, 8))
        
        ttk.Button(new_session_frame, text="Créer Session", 
                  command=self._create_session_for_date, style="Primary.TButton").pack(side="left")
        
        # Attendance section
        attendance_frame = ttk.LabelFrame(main_frame, text="Liste des Présences", padding="12")
        attendance_frame.pack(fill="both", expand=True, pady=(0, 8))
        
        # Session info
        self.session_info_label = ttk.Label(attendance_frame, text="Aucune session sélectionnée", 
                                           font=("Arial", 10, "bold"))
        self.session_info_label.pack(anchor="w", pady=(0, 8))
        
        # TreeView container frame
        tree_frame = ttk.Frame(attendance_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # Attendance treeview
        columns = ("student_id", "enrollment_no", "name", "status", "note")
        self.attendance_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        self.attendance_tree.heading("student_id", text="ID")
        self.attendance_tree.heading("enrollment_no", text="Matricule")
        self.attendance_tree.heading("name", text="Nom")
        self.attendance_tree.heading("status", text="Statut")
        self.attendance_tree.heading("note", text="Note")
        
        self.attendance_tree.column("student_id", width=60)
        self.attendance_tree.column("enrollment_no", width=120)
        self.attendance_tree.column("name", width=250)
        self.attendance_tree.column("status", width=100)
        self.attendance_tree.column("note", width=200)
        
        # Scrollbar
        attendance_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=attendance_scrollbar.set)
        
        self.attendance_tree.pack(side="left", fill="both", expand=True)
        attendance_scrollbar.pack(side="right", fill="y")
        
        # Actions frame (moved inside attendance_frame to ensure visibility)
        actions_frame = ttk.Frame(attendance_frame)
        actions_frame.pack(fill="x", pady=(12, 0))
        
        # Status buttons
        status_frame = ttk.LabelFrame(actions_frame, text="Marquer comme", padding="10")
        status_frame.pack(side="left", fill="y")
        
        ttk.Button(status_frame, text="Présent", 
                  command=lambda: self._set_attendance_status("Present")).pack(side="left", padx=(0, 6))
        ttk.Button(status_frame, text="Absent", 
                  command=lambda: self._set_attendance_status("Absent")).pack(side="left", padx=(0, 6))
        ttk.Button(status_frame, text="Retard", 
                  command=lambda: self._set_attendance_status("Late")).pack(side="left", padx=(0, 6))
        ttk.Button(status_frame, text="Justifié", 
                  command=lambda: self._set_attendance_status("Excused")).pack(side="left")
        
        # Other actions
        other_frame = ttk.Frame(actions_frame)
        other_frame.pack(side="right")
        
        ttk.Button(other_frame, text="Actualiser", 
                  command=self._load_attendance).pack(side="left", padx=(0, 8))
        ttk.Button(other_frame, text="Fermer", 
                  command=self.destroy).pack(side="left")

    def _load_sessions(self):
        """Load all sessions for the class"""
        try:
            sessions = list_sessions(self.class_id, limit=50)
            
            # Update combo box
            session_display = []
            self._sessions_data = {}
            
            for session in sessions:
                session_date = session["session_date"]
                display_text = f"{session_date} (ID: {session['id']})"
                session_display.append(display_text)
                self._sessions_data[display_text] = session
            
            self.session_combo["values"] = session_display
            
            # Select the most recent session if available
            if session_display:
                self.session_combo.set(session_display[0])
                self._on_session_selected()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les sessions: {str(e)}")

    def _on_session_selected(self, event=None):
        """Handle session selection from combo box"""
        selected = self.session_var.get()
        if selected and selected in self._sessions_data:
            session = self._sessions_data[selected]
            self._open_session(session["id"])

    def _create_session_for_date(self):
        """Create a new session for the specified date"""
        session_date = self.new_session_date_var.get().strip()
        if not session_date:
            messagebox.showinfo("Info", "Veuillez spécifier une date.")
            return
        
        try:
            session_id = get_or_create_session(self.class_id, session_date)
            
            # Auto-generate invoices for this session
            try:
                generate_invoices_for_session(self.class_id, session_id)
            except Exception:
                pass  # Non-blocking
            
            self._load_sessions()
            messagebox.showinfo("Succès", f"Nouvelle session créée pour {session_date}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création de la session: {str(e)}")

    def _open_session(self, session_id: int):
        """Open a specific session"""
        self.current_session_id = session_id
        
        # Update session info
        try:
            sessions = list_sessions(self.class_id)
            session_info = next((s for s in sessions if s["id"] == session_id), None)
            if session_info:
                self.session_info_label.config(text=f"Session du {session_info['session_date']} (ID: {session_id})")
        except Exception:
            self.session_info_label.config(text=f"Session ID: {session_id}")
        
        # Load attendance data
        self._load_attendance()

    def _load_attendance(self):
        """Load attendance data for current session"""
        if not self.current_session_id:
            return
        
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        try:
            # Ensure records exist for enrolled students
            ensure_records_for_enrolled(self.current_session_id, self.class_id, default_status="Present")
            
            # Load attendance data
            attendance_data = list_attendance(self.current_session_id)
            for record in attendance_data:
                name = f"{record['last_name']} {record['first_name']}"
                self.attendance_tree.insert("", "end", iid=record["student_id"], 
                                          values=(record["student_id"], record["enrollment_no"], 
                                                 name, record["status"], record["note"] or ""))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les présences: {str(e)}")

    def _set_attendance_status(self, status: str):
        """Set attendance status for selected students"""
        if not self.current_session_id:
            messagebox.showinfo("Info", "Veuillez sélectionner une session d'abord.")
            return
        
        selected_items = self.attendance_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Veuillez sélectionner au moins un élève.")
            return
        
        success_count = 0
        for item_id in selected_items:
            student_id = int(item_id)
            try:
                upsert_attendance(self.current_session_id, student_id, status)
                success_count += 1
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la mise à jour de l'élève {student_id}: {str(e)}")
        
        if success_count > 0:
            self._load_attendance()
            if self.on_attendance_changed:
                self.on_attendance_changed()

    def _delete_selected_session(self):
        """Delete the currently selected session"""
        selected = self.session_var.get()
        if not selected or selected not in self._sessions_data:
            messagebox.showinfo("Info", "Veuillez sélectionner une session à supprimer.")
            return
        
        session = self._sessions_data[selected]
        session_id = session["id"]
        session_date = session["session_date"]
        
        # Confirmation dialog with session details
        confirm_message = (f"Êtes-vous sûr de vouloir supprimer la session du {session_date}?\n\n"
                          f"Cette action supprimera définitivement:\n"
                          f"• Tous les enregistrements de présence\n"
                          f"• Toutes les factures associées à cette session\n\n"
                          f"Cette action ne peut pas être annulée.")
        
        if not messagebox.askyesno("Confirmer la suppression", confirm_message, icon="warning"):
            return
        
        try:
            # Delete the session
            delete_session(session_id)
            
            # Clear current session if it was the deleted one
            if self.current_session_id == session_id:
                self.current_session_id = None
                self.session_info_label.config(text="Aucune session sélectionnée")
                # Clear attendance tree
                for item in self.attendance_tree.get_children():
                    self.attendance_tree.delete(item)
            
            # Refresh sessions list
            self._load_sessions()
            
            messagebox.showinfo("Succès", f"Session du {session_date} supprimée avec succès.")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression de la session: {str(e)}")
