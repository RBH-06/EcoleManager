import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict
import os
import sqlite3
from datetime import datetime

from utils.config import (
    load_settings,
    save_settings,
    DB_PATH,
    GDRIVE_CREDENTIALS_PATH,
    GDRIVE_TOKEN_PATH,
)
from utils.theme import apply_dark_mode
from db.connection import get_connection
from utils.gdrive import google_deps_installed, build_service, ensure_folder, upload_file


class SettingsView(ttk.Frame):
    """Application settings. Some options are Admin-only."""

    def __init__(self, master, role_name: str, permissions: Optional[Dict[str, int]] = None):
        super().__init__(master)
        self.role_name = role_name
        self.permissions = permissions or {}
        self.settings = load_settings()
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        # Title
        header = ttk.Frame(self, style="Card.TFrame", padding=20)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
        ttk.Label(header, text="⚙️ Paramètres", style="CardTitle.TLabel", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Configurer l'application et les préférences", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(4,0))

        # Content container
        content = ttk.Frame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0,24))
        content.columnconfigure(0, weight=1)

        # General settings (visible to all)
        general = ttk.Frame(content, style="Card.TFrame", padding=16)
        general.grid(row=0, column=0, sticky="ew")
        general.columnconfigure(1, weight=1)

        ttk.Label(general, text="Année scolaire", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.academic_year_var = tk.StringVar(value=self.settings.get("academic_year", "2024-2025"))
        ttk.Entry(general, textvariable=self.academic_year_var, style="Modern.TEntry").grid(row=0, column=1, sticky="ew", padx=(12, 0))

        # Admin-only settings
        admin = ttk.Frame(content, style="Card.TFrame", padding=16)
        admin.grid(row=1, column=0, sticky="ew", pady=(12,0))
        admin.columnconfigure(1, weight=1)
        ttk.Label(admin, text="Paramètres Admin", style="CardTitle.TLabel", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        is_admin = (self.role_name == "Admin")

        # School name
        ttk.Label(admin, text="Nom de l'école", style="CardTitle.TLabel").grid(row=1, column=0, sticky="w")
        self.school_name_var = tk.StringVar(value=self.settings.get("school_name", "École Manager"))
        school_name_entry = ttk.Entry(admin, textvariable=self.school_name_var, style="Modern.TEntry")
        school_name_entry.grid(row=1, column=1, sticky="ew", padx=(12,0))
        if not is_admin:
            school_name_entry.state(["disabled"])  # only admin can edit

        # Dark mode toggle
        self.dark_mode_var = tk.BooleanVar(value=self.settings.get("dark_mode", False))
        dark_mode_chk = ttk.Checkbutton(admin, text="Activer mode sombre", variable=self.dark_mode_var)
        dark_mode_chk.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
        if not is_admin:
            dark_mode_chk.state(["disabled"])  # only admin can toggle

        # Additional useful settings (admin)
        ttk.Label(admin, text="Devise", style="CardTitle.TLabel").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.currency_var = tk.StringVar(value=self.settings.get("currency", "MAD"))
        currency_entry = ttk.Entry(admin, textvariable=self.currency_var, style="Modern.TEntry")
        currency_entry.grid(row=3, column=1, sticky="ew", padx=(12, 0))
        if not is_admin:
            currency_entry.state(["disabled"])  # only admin

        ttk.Label(admin, text="Fuseau horaire", style="CardTitle.TLabel").grid(row=4, column=0, sticky="w", pady=(8, 0))
        self.timezone_var = tk.StringVar(value=self.settings.get("timezone", "Africa/Casablanca"))
        timezone_entry = ttk.Entry(admin, textvariable=self.timezone_var, style="Modern.TEntry")
        timezone_entry.grid(row=4, column=1, sticky="ew", padx=(12, 0))
        if not is_admin:
            timezone_entry.state(["disabled"])  # only admin

        # Save & Backup buttons
        btns = ttk.Frame(content)
        btns.grid(row=2, column=0, sticky="e", pady=(12,0))
        save_btn = ttk.Button(btns, text="💾 Enregistrer", style="Primary.TButton", command=self._on_save)
        save_btn.grid(row=0, column=0)

        backup_btn = ttk.Button(btns, text="☁️ Sauvegarder sur Google Drive", command=self._on_backup_to_gdrive_api)
        backup_btn.grid(row=0, column=1, padx=(8, 0))
        if not is_admin:
            backup_btn.state(["disabled"])  # only admin can backup

    def _on_save(self):
        is_admin = (self.role_name == "Admin")
        # Always save general settings
        self.settings["academic_year"] = self.academic_year_var.get().strip() or "2024-2025"

        if is_admin:
            self.settings["school_name"] = self.school_name_var.get().strip() or "École Manager"
            self.settings["dark_mode"] = bool(self.dark_mode_var.get())
            self.settings["currency"] = self.currency_var.get().strip() or "MAD"
            self.settings["timezone"] = self.timezone_var.get().strip() or "Africa/Casablanca"
        else:
            # Non-admin cannot change admin fields; keep previous
            pass

        try:
            save_settings(self.settings)
            # Apply dark mode immediately if admin toggled it
            if is_admin:
                apply_dark_mode(self.settings.get("dark_mode", False))
            messagebox.showinfo("Succès", "Paramètres enregistrés.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _on_backup_to_gdrive_api(self):
        """Backup the SQLite DB and upload to Google Drive using Drive API.
        Requires OAuth client JSON placed at the configured path.
        """
        if not google_deps_installed():
            messagebox.showerror(
                "Google Drive",
                "Dépendances Google manquantes. Exécutez:\n"
                "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )
            return

        # Ensure DB file exists
        if not os.path.isfile(DB_PATH):
            messagebox.showerror("Erreur", "Base de données introuvable.")
            return

        # Ensure credentials exist or prompt user to choose/download
        if not os.path.exists(GDRIVE_CREDENTIALS_PATH):
            messagebox.showinfo(
                "Google Drive",
                "Fichier d'identifiants OAuth introuvable. Sélectionnez le fichier client_secret JSON téléchargé depuis Google Cloud Console.")
            chosen = filedialog.askopenfilename(
                title="Sélectionner le fichier d'identifiants Google (client_secret.json)",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if not chosen:
                return
            # Copy to app data path
            try:
                os.makedirs(os.path.dirname(GDRIVE_CREDENTIALS_PATH), exist_ok=True)
                import shutil
                shutil.copyfile(chosen, GDRIVE_CREDENTIALS_PATH)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'enregistrer les identifiants: {e}")
                return

        # Create a temporary local backup (consistent snapshot)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        tmp_dir = os.path.join(os.path.dirname(DB_PATH), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_backup_path = os.path.join(tmp_dir, f"ecole-{ts}.db")
        try:
            with get_connection() as conn:
                dest_conn = sqlite3.connect(tmp_backup_path)
                try:
                    conn.backup(dest_conn)
                finally:
                    dest_conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la création de la sauvegarde locale: {e}")
            return

        try:
            service = build_service(GDRIVE_CREDENTIALS_PATH, GDRIVE_TOKEN_PATH)
            # Ensure folder hierarchy: EcoleManager/Backups
            root_folder = ensure_folder(service, "EcoleManager")
            backups_folder = ensure_folder(service, "Backups", parent_id=root_folder)
            # Upload file
            dest_name = f"ecole-{ts}.db"
            meta = upload_file(service, backups_folder, tmp_backup_path, dest_name=dest_name)
            link = meta.get("webViewLink") or "(lien non disponible)"
            messagebox.showinfo("Succès", f"Sauvegarde uploadée sur Google Drive:\n{dest_name}\n{link}")
        except FileNotFoundError as e:
            messagebox.showerror("Google Drive", str(e))
        except Exception as e:
            messagebox.showerror("Google Drive", f"Échec de l'upload: {e}")
        finally:
            # Clean up temp backup
            try:
                if os.path.exists(tmp_backup_path):
                    os.remove(tmp_backup_path)
            except Exception:
                pass