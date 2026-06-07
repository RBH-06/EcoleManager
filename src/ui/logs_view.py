import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict
from services.log_service import list_logs

class LogsView(ttk.Frame):
    def __init__(self, master, role_name: str, permissions: Optional[Dict[str, int]] = None):
        super().__init__(master, padding=16)
        self.role_name = role_name
        self.permissions = permissions or {}
        self._build()
        self._reload()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Label(self, text="📜 Journaux du système (Audit)", style="CardTitle.TLabel", font=("Segoe UI", 14, "bold"))
        header.grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Enhanced filter controls
        self.user_filter = tk.StringVar()
        self.action_filter = tk.StringVar()
        self.category_filter = tk.StringVar()
        
        # Filters section with better layout
        filters_frame = ttk.LabelFrame(self, text="🔍 Filtres", padding=12)
        filters_frame.grid(row=0, column=0, sticky="ew", pady=(36, 16))
        filters_frame.columnconfigure(1, weight=1)
        filters_frame.columnconfigure(3, weight=1)
        filters_frame.columnconfigure(5, weight=1)
        
        # First row of filters
        ttk.Label(filters_frame, text="Utilisateur ID:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(filters_frame, textvariable=self.user_filter, width=12).grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=4)
        
        ttk.Label(filters_frame, text="Catégorie:").grid(row=0, column=2, sticky="w", padx=(0, 8), pady=4)
        self.category_combo = ttk.Combobox(filters_frame, textvariable=self.category_filter, 
                                          values=["Toutes", "📝 Présences", "💰 Paiements", "👥 Utilisateurs", "📚 Classes", "👤 Étudiants", "🔧 Système"], 
                                          state="readonly", width=16)
        self.category_combo.grid(row=0, column=3, sticky="ew", padx=(0, 16), pady=4)
        self.category_combo.set("Toutes")
        
        ttk.Label(filters_frame, text="Action contient:").grid(row=0, column=4, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(filters_frame, textvariable=self.action_filter, width=20).grid(row=0, column=5, sticky="ew", pady=4)
        
        # Second row for buttons
        button_frame = ttk.Frame(filters_frame)
        button_frame.grid(row=1, column=0, columnspan=6, pady=(12, 0))
        
        ttk.Button(button_frame, text="🔍 Rechercher", style="Primary.TButton", command=self._reload).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="🔄 Actualiser", command=self._reload).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="🧹 Effacer filtres", command=self._clear_filters).pack(side="left")

        # Table
        cols = ("timestamp", "username", "user_id", "action", "entity", "entity_id", "details")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=22, style="Modern.Treeview")
        headers = {
            "timestamp": "Date",
            "username": "Utilisateur",
            "user_id": "User ID",
            "action": "Action",
            "entity": "Entité",
            "entity_id": "Entité ID",
            "details": "Détails",
        }
        for c in cols:
            self.tree.heading(c, text=headers[c], anchor="w")
            if c in ("user_id", "entity_id"):
                self.tree.column(c, width=70, anchor="w")
            elif c == "timestamp":
                self.tree.column(c, width=160, anchor="w")
            elif c == "username":
                self.tree.column(c, width=120, anchor="w")
            elif c == "action":
                self.tree.column(c, width=160, anchor="w")
            else:
                self.tree.column(c, width=220, anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        # Scrollbars
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=1, column=1, sticky="ns")

    def _reload(self):
        # Clear
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Filters
        uid = None
        try:
            if self.user_filter.get().strip():
                uid = int(self.user_filter.get().strip())
        except ValueError:
            uid = None
        action_like = self.action_filter.get().strip().lower() or None

        # Determine allowed entities per category (use entity instead of action prefixes)
        category = self.category_filter.get().strip()
        allowed_entities = None
        if category and category != "Toutes":
            mapping_entities = {
                "📝 Présences": {"attendance", "session"},
                "💰 Paiements": {"payment"},
                "👥 Utilisateurs": {"user"},
                "📚 Classes": {"class"},
                "👤 Étudiants": {"student"},
                "🔧 Système": {"system"},
            }
            allowed_entities = mapping_entities.get(category)

        # Fetch first, then filter locally to allow combining filters
        logs = list_logs(limit=300, user_id=uid)
        for row in logs:
            action = row.get("action") or ""
            entity = row.get("entity") or ""

            # Apply action text filter (contains)
            if action_like and action_like not in action.lower():
                continue

            # Apply category filter by entity
            if allowed_entities is not None and entity not in allowed_entities:
                continue

            self.tree.insert("", "end", values=(
                row["timestamp"],
                row.get("username") or "",
                row.get("user_id") or "",
                action,
                entity,
                row.get("entity_id") or "",
                row.get("details") or "",
            ))

    def _clear_filters(self):
        self.user_filter.set("")
        self.action_filter.set("")
        if hasattr(self, "category_combo"):
            self.category_combo.set("Toutes")
        self._reload()