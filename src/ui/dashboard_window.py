import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict
from datetime import datetime

# Import theme colors for sidebar indicator fallback
from utils.theme import SIDEBAR_BG

ROLE_TITLES = {
    "Admin": "Tableau de bord - Admin",
    "Subadmin": "Tableau de bord - Subadmin",
}


class Sidebar(ttk.Frame):
    def __init__(self, master, on_nav, permissions: Optional[Dict[str, int]] = None):
        super().__init__(master, style="Sidebar.TFrame")
        self.on_nav = on_nav
        self.active_key = "home"
        self.permissions = permissions or {}
        self._build()

    def _set_active(self, key: str):
        self.active_key = key
        # Update all buttons and indicators
        for container in self.grid_slaves():
            for child in getattr(container, 'children', {}).values():
                if isinstance(child, ttk.Button) and hasattr(child, "_nav_key"):
                    is_active = (child._nav_key == key)
                    child.configure(style="SidebarSelected.TButton" if is_active else "Sidebar.TButton")
                    # Update the left indicator color
                    if hasattr(child, "_indicator"):
                        try:
                            child._indicator.configure(bg=(child._accent_color if is_active else "#1a1d29"))
                        except Exception:
                            pass

    def _build(self):
        self.columnconfigure(0, weight=1)
        
        # Modern brand header with gradient-like feel
        brand_frame = ttk.Frame(self, style="Sidebar.TFrame")
        brand_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        brand_frame.columnconfigure(0, weight=1)
        
        # App logo/icon with modern styling
        logo_text = "🎓"  # School graduation cap emoji
        logo = ttk.Label(brand_frame, text=logo_text, background="#1a1d29", foreground="#667eea", 
                        font=("Segoe UI", 24))
        logo.grid(row=0, column=0, pady=(20, 5))
        
        # App title with modern typography
        title = ttk.Label(brand_frame, text="École Manager", style="SidebarBrand.TLabel")
        title.grid(row=1, column=0, sticky="ew")
        
        # Subtitle/version
        subtitle = ttk.Label(brand_frame, text="v2.0", background="#1a1d29", 
                           foreground="#718096", font=("Segoe UI", 9))
        subtitle.grid(row=2, column=0, pady=(2, 10))

        # Navigation sections with modern icons
        nav_items = [
            ("🏠  Tableau de bord", "home", None, "#4299e1"),
            ("👥  Utilisateurs", "users", "can_manage_users", "#9f7aea"), 
            ("🎒  Élèves", "students", "can_manage_students", "#48bb78"),
            ("📚  Classes", "classes", "can_manage_classes", "#ed8936"),
            ("💰  Paiements", "fees", "can_manage_fees", "#f56565"),
            ("📜  Logs", "logs", "admin_only", "#4a5568"),
            ("🗒️  Notes", "notes", None, "#667eea"),
            ("📈  Rapports", "reports", None, "#38b2ac"),
            ("⚙️  Paramètres", "settings", None, "#718096"),
        ]

        r = 1
        for item in nav_items:
            text, key, permission, accent_color = item
            if permission == "admin_only" and getattr(self.master, 'role_name', 'Admin') != "Admin":
                continue
            if permission and permission != "admin_only" and not self.permissions.get(permission, False):
                continue  # Skip items the user doesn't have permission for
                
            # Row container to allow a left accent bar like web nav
            row_frame = ttk.Frame(self, style="Sidebar.TFrame")
            row_frame.grid(row=r, column=0, sticky="ew", padx=0, pady=2)
            row_frame.columnconfigure(1, weight=1)

            # Left accent bar indicates active
            indicator = tk.Frame(row_frame, width=4, height=36, bg=(accent_color if key == self.active_key else SIDEBAR_BG), highlightthickness=0)
            indicator.grid(row=0, column=0, sticky="nsw")

            btn = ttk.Button(
                row_frame,
                text=text,
                style="SidebarSelected.TButton" if key == self.active_key else "Sidebar.TButton",
                command=lambda k=key: (self.on_nav(k), self._set_active(k))
            )
            btn._nav_key = key
            btn._accent_color = accent_color
            btn.grid(row=0, column=1, sticky="ew", padx=(8, 8))

            # Hover effect: swap to hover style when mouse enters
            def on_enter(e, b=btn):
                if b._nav_key != self.active_key:
                    b.configure(style="SidebarHover.TButton")
            def on_leave(e, b=btn):
                if b._nav_key != self.active_key:
                    b.configure(style="Sidebar.TButton")
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

            # Keep reference to indicator for active updates
            btn._indicator = indicator

            r += 1
            
        # Add some bottom spacing
        spacer = ttk.Frame(self, style="Sidebar.TFrame")
        spacer.grid(row=r, column=0, sticky="nsew")
        self.rowconfigure(r, weight=1)


class Header(ttk.Frame):
    def __init__(self, master, role_name: str, on_logout):
        super().__init__(master, style="Header.TFrame")
        self.role_name = role_name
        self.on_logout = on_logout
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        
        # Left side - modern page title
        left = ttk.Frame(self, style="Header.TFrame")
        left.grid(row=0, column=0, sticky="ew", padx=(24, 0))
        
        title_text = ROLE_TITLES.get(self.role_name, "Tableau de bord")
        title_label = ttk.Label(left, text=title_text, style="HeaderTitle.TLabel")
        title_label.grid(row=0, column=0, sticky="w", pady=(12, 2))
        
        # Breadcrumb/user info
        user_info = f"👤 Connecté en tant que {self.role_name}"
        info_label = ttk.Label(left, text=user_info, style="HeaderMuted.TLabel")
        info_label.grid(row=1, column=0, sticky="w", pady=(0, 12))

        # Right side - modern logout button
        right = ttk.Frame(self, style="Header.TFrame")
        right.grid(row=0, column=1, sticky="e", padx=(0, 24), pady=12)
        
        logout_btn = ttk.Button(right, text="🚪 Se déconnecter", style="Header.TButton", command=self.on_logout)
        logout_btn.pack()


class HomeView(ttk.Frame):
    def __init__(self, master, role_name: str, permissions: Optional[Dict[str, int]] = None, on_navigate=None):
        super().__init__(master)
        self.role_name = role_name
        self.permissions = permissions or {}
        self.on_navigate = on_navigate
        self.stats = {}
        self.activities = []
        self._build()
        self._load_data()

    def _load_data(self):
        """Load real data from database"""
        try:
            from services.dashboard_service import get_dashboard_statistics, get_recent_activity, get_system_health
            self.stats = get_dashboard_statistics()
            # Only admins see recent activities
            if self.role_name == "Admin":
                self.activities = get_recent_activity(8)
            else:
                self.activities = []
            self.health = get_system_health()
            self._update_display()
        except Exception as e:
            # Fallback to placeholder data
            self.stats = {
                'total_students': 0, 'total_classes': 0, 'total_users': 0, 'total_sessions': 0,
                'recent_students': 0, 'recent_sessions': 0, 'recent_payments': 0
            }

    def _build(self):
        # Configure responsive grid
        self.rowconfigure(0, weight=0)  # Welcome banner
        self.rowconfigure(1, weight=0)  # Statistics cards
        self.rowconfigure(2, weight=1)  # Activity + Quick actions
        self.columnconfigure(0, weight=1)

        # Welcome banner with system info
        self._build_welcome_section()
        
        # Load school name from settings to reflect in header
        try:
            from utils.config import load_settings
            self._settings = load_settings()
        except Exception:
            self._settings = {"school_name": "École Manager"}
        
        # Statistics dashboard
        self._build_statistics_section()
        
        # Quick actions section (cleaner dashboard without activity feed)
        self._build_quick_actions_section()

    def _build_welcome_section(self):
        """Modern welcome banner with system status"""
        welcome_frame = ttk.Frame(self, style="CardAccent.TFrame", padding=24)
        welcome_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
        welcome_frame.columnconfigure(1, weight=1)
        
        # Welcome icon and text
        welcome_content = ttk.Frame(welcome_frame, style="CardAccent.TFrame")
        welcome_content.grid(row=0, column=0, sticky="w")
        
        icon = ttk.Label(welcome_content, text="🎓", background="#667eea", font=("Segoe UI", 32))
        icon.grid(row=0, column=0, padx=(0, 16))
        
        text_frame = ttk.Frame(welcome_content, style="CardAccent.TFrame")
        text_frame.grid(row=0, column=1)
        
        from utils.config import load_settings
        school_name = getattr(self, "_settings", None) and self._settings.get("school_name") or load_settings().get("school_name", "École Manager")
        ttk.Label(text_frame, text=f"Bonjour, {self.role_name}!", 
                 style="CardAccentTitle.TLabel", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(text_frame, text=f"{school_name} • Tableau de bord • {datetime.now().strftime('%d %B %Y')}", 
                 style="CardAccentMuted.TLabel").grid(row=1, column=0, sticky="w")
        
        # System status indicator
        status_frame = ttk.Frame(welcome_frame, style="CardAccent.TFrame")
        status_frame.grid(row=0, column=1, sticky="e")
        
        self.status_label = ttk.Label(status_frame, text="🟢 Système opérationnel", 
                                     style="CardAccentMuted.TLabel", font=("Segoe UI", 10))
        self.status_label.grid(row=0, column=0, padx=(0, 8))
        
        # Refresh button
        refresh_btn = ttk.Button(status_frame, text="🔄", command=self.refresh_data)
        refresh_btn.grid(row=0, column=1)

    def _build_statistics_section(self):
        """Statistics cards with real data"""
        stats_container = ttk.Frame(self)
        stats_container.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        
        # Configure columns for responsive layout
        for i in range(4):
            stats_container.columnconfigure(i, weight=1)
        
        # Statistics cards data
        self.stat_cards = []
        cards_config = [
            ("👥", "Élèves", "total_students", "recent_students", "#48bb78"),
            ("📚", "Classes", "total_classes", None, "#ed8936"), 
            ("📝", "Sessions", "total_sessions", "recent_sessions", "#4299e1"),
            ("💰", "Paiements", None, "recent_payments", "#f56565")
        ]
        
        for i, (icon, title, total_key, recent_key, color) in enumerate(cards_config):
            card = ttk.Frame(stats_container, style="Card.TFrame", padding=16)
            card.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0), pady=0, sticky="ew")
            
            # Icon with color background
            icon_frame = ttk.Frame(card, style="Card.TFrame")
            icon_frame.grid(row=0, column=0, columnspan=2, pady=(0, 12))
            
            icon_label = ttk.Label(icon_frame, text=icon, background="#ffffff", 
                                  foreground=color, font=("Segoe UI", 24))
            icon_label.grid(row=0, column=0)
            
            # Title
            ttk.Label(card, text=title, style="CardTitle.TLabel", 
                     font=("Segoe UI", 11, "bold")).grid(row=1, column=0, columnspan=2, sticky="w")
            
            # Total count (main number)
            if total_key:
                total_label = ttk.Label(card, text="0", style="CardTitle.TLabel", 
                                      font=("Segoe UI", 20, "bold"), foreground=color)
                total_label.grid(row=2, column=0, sticky="w", pady=(4, 0))
                self.stat_cards.append(('total', total_label, total_key))
                
                # Recent count (smaller, secondary)
                if recent_key:
                    recent_label = ttk.Label(card, text="+0 récents", style="Muted.TLabel", 
                                           font=("Segoe UI", 9))
                    recent_label.grid(row=3, column=0, sticky="w", pady=(2, 0))
                    self.stat_cards.append(('recent', recent_label, recent_key))
            else:
                # Only recent count (for payments)
                recent_label = ttk.Label(card, text="0", style="CardTitle.TLabel", 
                                       font=("Segoe UI", 20, "bold"), foreground=color)
                recent_label.grid(row=2, column=0, sticky="w", pady=(4, 0))
                ttk.Label(card, text="cette semaine", style="Muted.TLabel", 
                         font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", pady=(2, 0))
                self.stat_cards.append(('recent', recent_label, recent_key))

    def _build_quick_actions_section(self):
        """Clean quick actions panel with system info (no recent activity)."""
        actions_container = ttk.Frame(self)
        actions_container.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        actions_container.columnconfigure(0, weight=1)

        actions_card = ttk.Frame(actions_container, style="Card.TFrame", padding=20)
        actions_card.grid(row=0, column=0, sticky="nsew")
        actions_card.columnconfigure(0, weight=1)

        ttk.Label(actions_card, text="⚡ Actions rapides",
                 style="CardTitle.TLabel", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="ew", pady=(0, 16))

        actions_data = [
            ("👥 Ajouter Élève", "students", "can_manage_students"),
            ("📚 Nouvelle Classe", "classes", "can_manage_classes"),
            ("📝 Prendre Présence", "classes", "can_manage_attendance"),
            ("💰 Gérer Paiements", "fees", "can_manage_fees"),
            ("👤 Gérer Utilisateurs", "users", "can_manage_users"),
            ("🗒️ Ouvrir Notes", "notes", None),
        ]

        # Horizontal quick actions
        btns_frame = ttk.Frame(actions_card, style="Card.TFrame")
        btns_frame.grid(row=1, column=0, sticky="w")

        visible_actions = [a for a in actions_data if (a[2] is None) or self.permissions.get(a[2], False)]
        for col, (text, nav_key, _) in enumerate(visible_actions):
            btn = ttk.Button(btns_frame, text=text, style="Primary.TButton",
                             command=lambda k=nav_key: self.on_navigate(k) if self.on_navigate else None)
            btn.grid(row=0, column=col, padx=(0, 8), pady=(0, 0), sticky="w")

        info_frame = ttk.Frame(actions_card, style="Card.TFrame")
        info_frame.grid(row=2, column=0, sticky="ew", pady=(16, 0))

        ttk.Label(info_frame, text="💾 État Système",
                 style="CardTitle.TLabel", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")

        self.system_info_label = ttk.Label(info_frame, text="Chargement...",
                                          style="Muted.TLabel", font=("Segoe UI", 9))
        self.system_info_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _update_display(self):
        """Update display with loaded data"""
        # Update statistics cards
        for card_type, label, key in self.stat_cards:
            if card_type == 'total':
                value = self.stats.get(key, 0)
                label.configure(text=str(value))
            elif card_type == 'recent':
                value = self.stats.get(key, 0)
                if key == 'recent_payments':
                    label.configure(text=str(value))
                else:
                    label.configure(text=f"+{value} récents")
        
        # Activity feed removed for a cleaner dashboard
        
        # Update system status
        if hasattr(self, 'health'):
            total_records = self.health.get('total_records', 0)
            active_sessions = self.health.get('active_sessions', 0)
            self.system_info_label.configure(
                text=f"Base de données: {total_records} enregistrements\nSessions actives: {active_sessions}"
            )

    def _update_activity_feed(self):
        """Update the activity feed with real data"""
        # Clear existing content
        for widget in self.activity_container.winfo_children():
            widget.destroy()
        
        if not self.activities:
            ttk.Label(self.activity_container, text="Aucune activité récente", 
                     style="Muted.TLabel").grid(row=0, column=0, sticky="w")
            return
        
        # Add activity items with enhanced display
        for i, activity in enumerate(self.activities[:8]):  # Limit to 8 items
            activity_item = ttk.Frame(self.activity_container, style="Card.TFrame")
            activity_item.grid(row=i, column=0, sticky="ew", pady=(0, 8))
            activity_item.columnconfigure(1, weight=1)
            
            # Icon and color based on activity type
            icon_colors = {
                'student_new': ('👥', '#48bb78'),
                'class_new': ('📚', '#ed8936'),
                'session_new': ('📝', '#4299e1'),
                'payment_received': ('💰', '#f56565'),
                'user_new': ('👤', '#9f7aea'),
                'enrollment_new': ('📊', '#38b2ac'),
                'attendance_updated': ('✅', '#68d391'),
                'fee_rule_updated': ('💳', '#fc8181'),
            }
            
            icon, color = icon_colors.get(activity['type'], ('📋', '#718096'))
            
            # Priority indicator (dot color)
            priority_colors = {'high': '#f56565', 'medium': '#ed8936', 'low': '#718096'}
            priority_color = priority_colors.get(activity.get('priority', 'medium'), '#718096')
            
            # Icon with colored background
            icon_frame = ttk.Frame(activity_item, style="Card.TFrame")
            icon_frame.grid(row=0, column=0, padx=(0, 12))
            
            ttk.Label(icon_frame, text=icon, background="#ffffff", 
                     foreground=color, font=("Segoe UI", 16)).grid(row=0, column=0)
            
            # Priority dot (small indicator)
            priority_dot = ttk.Label(icon_frame, text="●", background="#ffffff",
                                   foreground=priority_color, font=("Segoe UI", 8))
            priority_dot.grid(row=1, column=0)
            
            # Activity text
            text_frame = ttk.Frame(activity_item, style="Card.TFrame")
            text_frame.grid(row=0, column=1, sticky="ew")
            
            # Action text with enhanced formatting
            action_text = activity['action']
            if len(action_text) > 60:  # Truncate long messages
                action_text = action_text[:57] + "..."
                
            ttk.Label(text_frame, text=action_text, 
                     style="CardTitle.TLabel", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
            
            # Timestamp with relative time
            try:
                timestamp = datetime.fromisoformat(activity['timestamp'])
                now = datetime.now()
                diff = now - timestamp
                
                if diff.days > 0:
                    time_str = f"Il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
                elif diff.seconds > 3600:
                    hours = diff.seconds // 3600
                    time_str = f"Il y a {hours}h"
                elif diff.seconds > 60:
                    minutes = diff.seconds // 60
                    time_str = f"Il y a {minutes}min"
                else:
                    time_str = "À l'instant"
            except:
                time_str = "Récemment"
                
            ttk.Label(text_frame, text=time_str, 
                     style="Muted.TLabel", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w")

    def refresh_data(self):
        """Refresh dashboard data"""
        self._load_data()


class DashboardWindow(tk.Frame):
    def __init__(self, master, user_id: int, role_name: str, permissions: Optional[Dict[str, int]] = None):
        super().__init__(master)
        self.master = master
        self.user_id = user_id
        self.role_name = role_name
        self.permissions = permissions or {}
        self._build()

    def _build(self):
        # Configure responsive grid
        self.rowconfigure(0, weight=0)  # Header row - fixed height
        self.rowconfigure(1, weight=1)  # Content row - expandable
        self.columnconfigure(0, weight=0)  # Sidebar column - fixed width
        self.columnconfigure(1, weight=1)  # Main content column - expandable

        # Sidebar with fixed width
        self.sidebar = Sidebar(self, on_nav=self._navigate, permissions=self.permissions)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.configure(width=280)  # Fixed sidebar width

        # Header
        self.header = Header(self, role_name=self.role_name, on_logout=self._logout)
        self.header.grid(row=0, column=1, sticky="ew")

        # Content area - fully responsive
        self.content = ttk.Frame(self)
        self.content.grid(row=1, column=1, sticky="nsew", padx=24, pady=24)
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        # Default view
        self._show_view(HomeView)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_view(self, view_cls):
        self._clear_content()
        # Pass permissions and navigation to views
        if view_cls == HomeView:
            view = view_cls(self.content, role_name=self.role_name, permissions=self.permissions, on_navigate=self._navigate)
        else:
            view = view_cls(self.content, role_name=self.role_name, permissions=self.permissions)
        view.grid(row=0, column=0, sticky="nsew")
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

    def _navigate(self, key: str):
        # Navigation mapping
        if key == "students":
            from ui.students_view import StudentsView
            self._clear_content()
            view = StudentsView(self.content, current_user_id=self.user_id)
            view.grid(row=0, column=0, sticky="nsew")
            self.content.rowconfigure(0, weight=1)
            self.content.columnconfigure(0, weight=1)
        elif key == "classes":
            from ui.classes_view import ClassesView
            self._clear_content()
            view = ClassesView(self.content, permissions=self.permissions)
            view.grid(row=0, column=0, sticky="nsew")
            self.content.rowconfigure(0, weight=1)
            self.content.columnconfigure(0, weight=1)
        elif key == "fees":
            from ui.fees_view import FeesView
            self._clear_content()
            view = FeesView(self.content, current_user_id=self.user_id)
            view.grid(row=0, column=0, sticky="nsew")
            self.content.rowconfigure(0, weight=1)
            self.content.columnconfigure(0, weight=1)
        elif key == "users":
            from ui.users_view import UsersView
            self._clear_content()
            view = UsersView(self.content)
            view.grid(row=0, column=0, sticky="nsew")
            self.content.rowconfigure(0, weight=1)
            self.content.columnconfigure(0, weight=1)
        elif key == "logs" and self.role_name == "Admin":
            from ui.logs_view import LogsView
            self._clear_content()
            view = LogsView(self.content, role_name=self.role_name, permissions=self.permissions)
            view.grid(row=0, column=0, sticky="nsew")
            self.content.rowconfigure(0, weight=1)
            self.content.columnconfigure(0, weight=1)
        elif key == "settings":
            from ui.settings_view import SettingsView
            self._clear_content()
            view = SettingsView(self.content, role_name=self.role_name, permissions=self.permissions)
            view.grid(row=0, column=0, sticky="nsew")
            self.content.rowconfigure(0, weight=1)
            self.content.columnconfigure(0, weight=1)
        elif key == "notes":
            from ui.notes_view import NotesView
            self._clear_content()
            view = NotesView(self.content, role_name=self.role_name, permissions=self.permissions)
            view.grid(row=0, column=0, sticky="nsew")
            self.content.rowconfigure(0, weight=1)
            self.content.columnconfigure(0, weight=1)
        elif key == "reports":
            from ui.reports_view import ReportsView
            self._clear_content()
            view = ReportsView(self.content, role_name=self.role_name, permissions=self.permissions)
            view.grid(row=0, column=0, sticky="nsew")
            self.content.rowconfigure(0, weight=1)
            self.content.columnconfigure(0, weight=1)
        else:
            self._show_view(HomeView)
        
        # Update sidebar active state
        if hasattr(self, 'sidebar'):
            self.sidebar._set_active(key)

    def _logout(self):
        from ui.login_window import LoginWindow
        for widget in self.master.winfo_children():
            widget.destroy()
        login = LoginWindow(self.master)
        login.pack(fill="both", expand=True)