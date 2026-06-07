import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict

from services.auth_service import authenticate
from ui.dashboard_window import DashboardWindow


class LoginWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self._build()

    def _build(self):
        # Configure responsive layout
        self.columnconfigure(0, weight=2)  # Left side (hero section)
        self.columnconfigure(1, weight=1)  # Right side (login form)
        self.rowconfigure(0, weight=1)

        # Left side - Hero section with gradient background
        hero_section = ttk.Frame(self, style="CardAccent.TFrame")
        hero_section.grid(row=0, column=0, sticky="nsew")
        hero_section.columnconfigure(0, weight=1)
        hero_section.rowconfigure(0, weight=1)
        
        # Hero content container
        hero_content = ttk.Frame(hero_section, style="CardAccent.TFrame")
        hero_content.grid(row=0, column=0, sticky="nsew", padx=60, pady=60)
        hero_content.columnconfigure(0, weight=1)
        hero_content.rowconfigure(1, weight=1)
        
        # Hero header
        hero_header = ttk.Frame(hero_content, style="CardAccent.TFrame")
        hero_header.grid(row=0, column=0, sticky="ew", pady=(0, 40))
        
        # App logo/icon (image with fallback)
        try:
            from tkinter import PhotoImage
            from utils.resources import get_resource_path
            logo_path = get_resource_path('src/assets/web-app-manifest-512x512.png')
            if os.path.exists(logo_path):
                self._logo_img = PhotoImage(file=logo_path)  # keep reference
                logo = ttk.Label(hero_header, image=self._logo_img, background="#667eea")
            else:
                logo = ttk.Label(hero_header, text="🎓", background="#667eea", 
                                font=("Segoe UI", 72), foreground="#ffffff")
        except Exception:
            logo = ttk.Label(hero_header, text="🎓", background="#667eea", 
                            font=("Segoe UI", 72), foreground="#ffffff")
        logo.grid(row=0, column=0, pady=(0, 20))
        
        # Hero title
        hero_title = ttk.Label(hero_header, text="École Manager", 
                              style="CardAccentTitle.TLabel",
                              font=("Segoe UI", 32, "bold"))
        hero_title.grid(row=1, column=0)
        
        # Hero subtitle
        hero_subtitle = ttk.Label(hero_header, 
                                 text="Plateforme moderne de gestion scolaire",
                                 style="CardAccentMuted.TLabel",
                                 font=("Segoe UI", 16))
        hero_subtitle.grid(row=2, column=0, pady=(10, 0))
        
        # Hero features
        features_frame = ttk.Frame(hero_content, style="CardAccent.TFrame")
        features_frame.grid(row=1, column=0, sticky="w")
        
        features = [
            "✨ Interface moderne et intuitive",
            "📊 Tableaux de bord en temps réel", 
            "💰 Gestion simplifiée des paiements",
            "🔒 Sécurité et contrôle d'accès",
            "📱 Design responsive"
        ]
        
        for i, feature in enumerate(features):
            feature_label = ttk.Label(features_frame, text=feature,
                                     style="CardAccentMuted.TLabel",
                                     font=("Segoe UI", 12))
            feature_label.grid(row=i, column=0, sticky="w", pady=8)

        # Right side - Login form
        login_section = ttk.Frame(self, style="Card.TFrame")
        login_section.grid(row=0, column=1, sticky="nsew")
        login_section.columnconfigure(0, weight=1)
        login_section.rowconfigure(0, weight=1)
        
        # Login container
        login_container = ttk.Frame(login_section, style="Card.TFrame")
        login_container.grid(row=0, column=0, sticky="nsew", padx=48, pady=60)
        login_container.columnconfigure(0, weight=1)
        
        # Login header
        login_title = ttk.Label(login_container, text="Connexion", 
                               style="CardTitle.TLabel",
                               font=("Segoe UI", 24, "bold"))
        login_title.grid(row=0, column=0, pady=(0, 8), sticky="w")
        
        login_subtitle = ttk.Label(login_container, 
                                  text="Accédez à votre tableau de bord",
                                  style="Muted.TLabel",
                                  font=("Segoe UI", 12))
        login_subtitle.grid(row=1, column=0, pady=(0, 32), sticky="w")
        
        # Username field
        username_frame = ttk.Frame(login_container, style="Card.TFrame")
        username_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        username_frame.columnconfigure(0, weight=1)
        
        ttk.Label(username_frame, text="Nom d'utilisateur", 
                 style="CardTitle.TLabel", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self.username_var, 
                                  font=("Segoe UI", 12), style="Modern.TEntry")
        username_entry.grid(row=1, column=0, sticky="ew", ipady=12)
        username_entry.focus()
        
        # Password field  
        password_frame = ttk.Frame(login_container, style="Card.TFrame")
        password_frame.grid(row=3, column=0, sticky="ew", pady=(0, 32))
        password_frame.columnconfigure(0, weight=1)
        
        ttk.Label(password_frame, text="Mot de passe",
                 style="CardTitle.TLabel", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="*",
                                  font=("Segoe UI", 12), style="Modern.TEntry")
        password_entry.grid(row=1, column=0, sticky="ew", ipady=12)
        
        # Login button
        login_btn = ttk.Button(login_container, text="🚀 Se connecter", 
                              style="Primary.TButton", command=self._on_login)
        login_btn.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        
        # Footer info
        footer = ttk.Label(login_container, 
                          text="Version 2.0 • École Manager © 2024",
                          style="Muted.TLabel", font=("Segoe UI", 9))
        footer.grid(row=5, column=0, pady=(20, 0))
        
        # Bind Enter key to login
        self.master.bind('<Return>', lambda e: self._on_login())

    def _on_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        # Enhanced validation
        from utils.validation import sanitize_input
        
        # Sanitize inputs
        username = sanitize_input(username)
        password = sanitize_input(password)
        
        if not username or not password:
            messagebox.showwarning("Champs requis", "Veuillez saisir le nom d'utilisateur et le mot de passe.")
            return
            
        # Basic length checks for security
        if len(username) > 50:
            messagebox.showerror("Erreur", "Nom d'utilisateur trop long.")
            return
            
        if len(password) > 128:
            messagebox.showerror("Erreur", "Mot de passe trop long.")
            return
        
        try:
            user_id, role_name, permissions = authenticate(username, password)
            # Log login action
            try:
                from services.log_service import log_action
                log_action("user_login", user_id=user_id, entity="user", entity_id=user_id, details=f"role={role_name}")
            except Exception:
                pass
            # Navigate to dashboard with permissions
            self._open_dashboard(user_id, role_name, permissions)
        except Exception as e:
            messagebox.showerror("Échec de connexion", str(e))

    def _open_dashboard(self, user_id: int, role_name: str, permissions: Optional[Dict[str, int]]):
        # Pass permissions to the dashboard
        dashboard = DashboardWindow(self.master, user_id=user_id, role_name=role_name, permissions=permissions)
        dashboard.pack(fill="both", expand=True)
        self.destroy()