import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, List
from db.connection import get_connection

class NotesView(ttk.Frame):
    """Simple admin notes/to-do board with statuses and priorities.
    - Columns: Title, Status, Priority, Updated At
    - CRUD: add, update (inline), delete
    """
    def __init__(self, master, role_name: str, permissions: Optional[Dict[str, int]] = None):
        super().__init__(master, padding=16)
        self.role_name = role_name
        self.permissions = permissions or {}
        self._build()
        self._reload()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Label(self, text="🗒️ Notes d'Admin / To-Do", style="CardTitle.TLabel", font=("Segoe UI", 14, "bold"))
        header.grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Form
        form = ttk.LabelFrame(self, text="Ajouter / Modifier", padding=12)
        form.grid(row=0, column=0, sticky="ew", pady=(36, 12))
        for i in (1, 3):
            form.columnconfigure(i, weight=1)

        ttk.Label(form, text="Titre:").grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.title_var).grid(row=0, column=1, sticky="ew", padx=(6, 16))

        ttk.Label(form, text="Statut:").grid(row=0, column=2, sticky="w")
        self.status_var = tk.StringVar(value="todo")
        status_combo = ttk.Combobox(form, textvariable=self.status_var, values=["todo", "doing", "done"], state="readonly", width=10)
        status_combo.grid(row=0, column=3, sticky="w", padx=(6, 16))

        ttk.Label(form, text="Priorité:").grid(row=0, column=4, sticky="w")
        self.priority_var = tk.StringVar(value="normal")
        priority_combo = ttk.Combobox(form, textvariable=self.priority_var, values=["low", "normal", "high"], state="readonly", width=10)
        priority_combo.grid(row=0, column=5, sticky="w", padx=(6, 16))

        ttk.Label(form, text="Contenu:").grid(row=1, column=0, sticky="nw", pady=(8,0))
        self.content_text = tk.Text(form, height=4)
        self.content_text.grid(row=1, column=1, columnspan=5, sticky="ew", pady=(8,0))

        btns = ttk.Frame(form)
        btns.grid(row=2, column=0, columnspan=6, pady=(12, 0), sticky="w")
        ttk.Button(btns, text="➕ Ajouter", style="Primary.TButton", command=self._add_note).pack(side="left", padx=(0,8))
        ttk.Button(btns, text="💾 Mettre à jour", command=self._update_selected).pack(side="left", padx=(0,8))
        ttk.Button(btns, text="🗑️ Supprimer", command=self._delete_selected).pack(side="left")

        # Table
        cols = ("id", "title", "status", "priority", "updated_at")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18, style="Modern.Treeview")
        headers = {
            "id": "ID",
            "title": "Titre",
            "status": "Statut",
            "priority": "Priorité",
            "updated_at": "Mis à jour",
        }
        for c in cols:
            self.tree.heading(c, text=headers[c], anchor="w")
            if c == "id":
                self.tree.column(c, width=60, anchor="w")
            elif c == "updated_at":
                self.tree.column(c, width=160, anchor="w")
            elif c == "title":
                self.tree.column(c, width=300, anchor="w")
            else:
                self.tree.column(c, width=120, anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        # Scrollbar
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=1, column=1, sticky="ns")

        # Row select -> load into form
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Filters
        filters = ttk.Frame(self)
        filters.grid(row=2, column=0, sticky="ew", pady=(8,0))
        ttk.Label(filters, text="Filtrer par statut:").pack(side="left")
        self.filter_status = tk.StringVar(value="all")
        ttk.Combobox(filters, textvariable=self.filter_status, values=["all", "todo", "doing", "done"], state="readonly", width=10).pack(side="left", padx=6)
        ttk.Button(filters, text="Appliquer", command=self._reload).pack(side="left")

    def _query_notes(self) -> List[dict]:
        conn = get_connection()
        try:
            sql = "SELECT id, title, content, status, priority, updated_at FROM admin_notes"
            params = []
            if self.filter_status.get() != "all":
                sql += " WHERE status = ?"
                params.append(self.filter_status.get())
            sql += " ORDER BY CASE status WHEN 'todo' THEN 0 WHEN 'doing' THEN 1 ELSE 2 END, priority DESC, updated_at DESC"
            cur = conn.execute(sql, tuple(params))
            keys = ["id", "title", "content", "status", "priority", "updated_at"]
            return [dict(zip(keys, row)) for row in cur.fetchall()]
        finally:
            conn.close()

    def _reload(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in self._query_notes():
            self.tree.insert("", "end", values=(row["id"], row["title"] or "(Sans titre)", row["status"], row["priority"], row["updated_at"]))

    def _on_select(self, event=None):
        item = self.tree.selection()
        if not item:
            return
        values = self.tree.item(item[0], "values")
        note_id, title, status, priority, _ = values
        self.title_var.set(title)
        self.status_var.set(status)
        self.priority_var.set(priority)
        # Load content
        conn = get_connection()
        try:
            row = conn.execute("SELECT content FROM admin_notes WHERE id=?", (note_id,)).fetchone()
            self.content_text.delete("1.0", "end")
            if row:
                self.content_text.insert("1.0", row[0] or "")
        finally:
            conn.close()

    def _add_note(self):
        title = self.title_var.get().strip()
        content = self.content_text.get("1.0", "end").strip()
        status = self.status_var.get()
        priority = self.priority_var.get()
        if not content:
            messagebox.showwarning("Validation", "Le contenu est obligatoire.")
            return
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO admin_notes(title, content, status, priority) VALUES(?,?,?,?)",
                (title, content, status, priority),
            )
            conn.commit()
        finally:
            conn.close()
        self._clear_form()
        self._reload()

    def _update_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionnez une note à mettre à jour.")
            return
        note_id = self.tree.item(sel[0], "values")[0]
        title = self.title_var.get().strip()
        content = self.content_text.get("1.0", "end").strip()
        status = self.status_var.get()
        priority = self.priority_var.get()
        if not content:
            messagebox.showwarning("Validation", "Le contenu est obligatoire.")
            return
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE admin_notes SET title=?, content=?, status=?, priority=?, updated_at=datetime('now') WHERE id=?",
                (title, content, status, priority, note_id),
            )
            conn.commit()
        finally:
            conn.close()
        self._reload()

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        note_id = self.tree.item(sel[0], "values")[0]
        if not messagebox.askyesno("Confirmer", "Supprimer cette note ?"):
            return
        conn = get_connection()
        try:
            conn.execute("DELETE FROM admin_notes WHERE id=?", (note_id,))
            conn.commit()
        finally:
            conn.close()
        self._reload()

    def _clear_form(self):
        self.title_var.set("")
        self.status_var.set("todo")
        self.priority_var.set("normal")
        self.content_text.delete("1.0", "end")