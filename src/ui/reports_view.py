import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, List, Any
from datetime import datetime, date
from db.connection import get_connection

# Optional dependencies
try:
    from tkcalendar import DateEntry  # type: ignore
except Exception:  # pragma: no cover
    DateEntry = None  # Fallback handled below

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
    from matplotlib.figure import Figure  # type: ignore
except Exception:  # pragma: no cover
    Figure = None
    FigureCanvasTkAgg = None


# -------------------------------
# DB helper
# -------------------------------

def query_all(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        conn.close()


# -------------------------------
# UI helpers
# -------------------------------
class DateInput(ttk.Frame):
    """Date picker: uses tkcalendar.DateEntry if available, otherwise Spinbox Y/M/D."""
    def __init__(self, master, initial: Optional[date] = None):
        super().__init__(master)
        initial = initial or date.today()
        if DateEntry is not None:
            self._widget_type = 'dateentry'
            self._w = DateEntry(self, date_pattern='yyyy-mm-dd')
            self._w.set_date(initial)
            self._w.grid(row=0, column=0, sticky='ew')
        else:
            self._widget_type = 'spins'
            self.columnconfigure(0, weight=1)
            self.year = tk.IntVar(value=initial.year)
            self.month = tk.IntVar(value=initial.month)
            self.day = tk.IntVar(value=initial.day)
            y = ttk.Spinbox(self, from_=2000, to=2100, textvariable=self.year, width=6)
            m = ttk.Spinbox(self, from_=1, to=12, textvariable=self.month, width=4)
            d = ttk.Spinbox(self, from_=1, to=31, textvariable=self.day, width=4)
            ttk.Label(self, text='Y').grid(row=0, column=0, padx=(0,2))
            y.grid(row=0, column=1)
            ttk.Label(self, text='M').grid(row=0, column=2, padx=(6,2))
            m.grid(row=0, column=3)
            ttk.Label(self, text='D').grid(row=0, column=4, padx=(6,2))
            d.grid(row=0, column=5)

    def get(self) -> str:
        if getattr(self, '_widget_type', '') == 'dateentry':
            try:
                d = self._w.get_date()  # type: ignore[attr-defined]
                return d.strftime('%Y-%m-%d')
            except Exception:
                return date.today().strftime('%Y-%m-%d')
        # spins
        try:
            y, m, d = int(self.year.get()), int(self.month.get()), int(self.day.get())
            dt = date(y, m, d)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return date.today().strftime('%Y-%m-%d')


class ReportsView(ttk.Frame):
    """Comprehensive reports with charts and proper date pickers."""

    def __init__(self, master, role_name: str, permissions: Optional[Dict[str, int]] = None):
        super().__init__(master, padding=16)
        self.role_name = role_name
        self.permissions = permissions or {}

        # Shared date range
        today = date.today()
        month_start = today.replace(day=1)
        self.start_input = None  # set in builders
        self.end_input = None
        self._build(month_start, today)

        # Initial loads
        self._load_overview()
        self._reload_attendance()
        self._reload_payments()
        self._reload_top_classes()
        self._render_charts()

    # ================= BUILD UI =================
    def _build(self, start: date, end: date):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        title = ttk.Label(self, text="📈 Statistiques & Rapports", style="CardTitle.TLabel", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 12))

        # Notebook for sections
        self.nb = ttk.Notebook(self)
        self.nb.grid(row=1, column=0, sticky="nsew")

        # Tabs
        self.tab_overview = ttk.Frame(self.nb)
        self.tab_attendance = ttk.Frame(self.nb)
        self.tab_payments = ttk.Frame(self.nb)
        self.tab_classes = ttk.Frame(self.nb)

        self.nb.add(self.tab_overview, text="Vue d'ensemble")
        self.nb.add(self.tab_attendance, text="Assiduité")
        self.nb.add(self.tab_payments, text="Paiements")
        self.nb.add(self.tab_classes, text="Classes")

        # Build each tab
        self._build_overview_tab(self.tab_overview)
        self._build_attendance_tab(self.tab_attendance, start, end)
        self._build_payments_tab(self.tab_payments, start, end)
        self._build_classes_tab(self.tab_classes)

    def _build_overview_tab(self, parent: ttk.Frame):
        parent.columnconfigure(0, weight=1)

        # KPI row
        kpi_row = ttk.Frame(parent)
        kpi_row.grid(row=0, column=0, sticky="ew", pady=(4, 12))
        for i in range(4):
            kpi_row.columnconfigure(i, weight=1)

        self.kpi_vars = {
            'students': tk.StringVar(value='0'),
            'classes': tk.StringVar(value='0'),
            'sessions': tk.StringVar(value='0'),
            'payments_paid': tk.StringVar(value='0'),
        }
        config = [
            ("👥", "Élèves", 'students', '#48bb78'),
            ("📚", "Classes", 'classes', '#ed8936'),
            ("📝", "Séances", 'sessions', '#4299e1'),
            ("💰", "Paiements (payés)", 'payments_paid', '#f56565'),
        ]
        for i, (icon, title, key, color) in enumerate(config):
            card = ttk.Frame(kpi_row, style="Card.TFrame", padding=14)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0))
            ttk.Label(card, text=icon, background="#ffffff", foreground=color, font=("Segoe UI", 22)).grid(row=0, column=0, sticky='w')
            ttk.Label(card, text=title, style="CardTitle.TLabel", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky='w')
            ttk.Label(card, textvariable=self.kpi_vars[key], style="CardTitle.TLabel", font=("Segoe UI", 18, "bold"), foreground=color).grid(row=2, column=0, sticky='w')

        # Charts area
        charts = ttk.Frame(parent)
        charts.grid(row=1, column=0, sticky="nsew")
        charts.columnconfigure(0, weight=1)
        charts.columnconfigure(1, weight=1)
        charts.rowconfigure(0, weight=1)

        # Placeholders for canvases
        self._chart_payment = ttk.Frame(charts, style="Card.TFrame")
        self._chart_payment.grid(row=0, column=0, sticky='nsew', padx=(0, 6))
        self._chart_attendance = ttk.Frame(charts, style="Card.TFrame")
        self._chart_attendance.grid(row=0, column=1, sticky='nsew', padx=(6, 0))

    def _build_attendance_tab(self, parent: ttk.Frame, start: date, end: date):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        # Filters
        f = ttk.LabelFrame(parent, text="Filtres", padding=10)
        f.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for i in (1, 3):
            f.columnconfigure(i, weight=1)

        ttk.Label(f, text="Date début:").grid(row=0, column=0, sticky='w')
        self.start_input = DateInput(f, initial=start)
        self.start_input.grid(row=0, column=1, sticky='w', padx=(6, 16))

        ttk.Label(f, text="Date fin:").grid(row=0, column=2, sticky='w')
        self.end_input = DateInput(f, initial=end)
        self.end_input.grid(row=0, column=3, sticky='w', padx=(6, 16))

        ttk.Button(f, text="Appliquer", style="Primary.TButton", command=self._apply_filters).grid(row=0, column=4)

        # Summary row
        self.attendance_summary = ttk.Label(parent, text="", style="Muted.TLabel")
        self.attendance_summary.grid(row=1, column=0, sticky='w', pady=(0, 6))

        # Table
        cols = ("class_name", "total_records", "Present", "Absent", "Late", "Excused")
        self.att_tree = ttk.Treeview(parent, columns=cols, show="headings", style="Modern.Treeview")
        for c in cols:
            self.att_tree.heading(c, text=c, anchor='w')
            self.att_tree.column(c, width=120 if c != 'class_name' else 220, anchor='w')
        self.att_tree.grid(row=2, column=0, sticky='nsew')
        yscroll = ttk.Scrollbar(parent, orient='vertical', command=self.att_tree.yview)
        self.att_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=2, column=1, sticky='ns')

        ttk.Button(parent, text="Exporter CSV", command=lambda: self._export_csv(self.att_tree, "attendance_report.csv")).grid(row=3, column=0, sticky='e', pady=(6, 0))

    def _build_payments_tab(self, parent: ttk.Frame, start: date, end: date):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        # Filters
        f = ttk.LabelFrame(parent, text="Filtres", padding=10)
        f.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for i in (1, 3):
            f.columnconfigure(i, weight=1)

        ttk.Label(f, text="Date début:").grid(row=0, column=0, sticky='w')
        self.start_input_pay = DateInput(f, initial=start)
        self.start_input_pay.grid(row=0, column=1, sticky='w', padx=(6, 16))

        ttk.Label(f, text="Date fin:").grid(row=0, column=2, sticky='w')
        self.end_input_pay = DateInput(f, initial=end)
        self.end_input_pay.grid(row=0, column=3, sticky='w', padx=(6, 16))

        ttk.Button(f, text="Appliquer", style="Primary.TButton", command=self._apply_filters_pay).grid(row=0, column=4)

        # Summary
        self.pay_summary = ttk.Label(parent, text="", style="Muted.TLabel")
        self.pay_summary.grid(row=1, column=0, sticky='w', pady=(0, 6))

        # Table
        cols = ("status", "count", "total_amount")
        self.pay_tree = ttk.Treeview(parent, columns=cols, show="headings", style="Modern.Treeview")
        for c in cols:
            self.pay_tree.heading(c, text=c, anchor='w')
            self.pay_tree.column(c, width=160 if c != 'status' else 200, anchor='w')
        self.pay_tree.grid(row=2, column=0, sticky='nsew')
        yscroll = ttk.Scrollbar(parent, orient='vertical', command=self.pay_tree.yview)
        self.pay_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=2, column=1, sticky='ns')

        ttk.Button(parent, text="Exporter CSV", command=lambda: self._export_csv(self.pay_tree, "payments_report.csv")).grid(row=3, column=0, sticky='e', pady=(6, 0))

    def _build_classes_tab(self, parent: ttk.Frame):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        cols = ("class_name", "level", "enrollment_count")
        self.top_tree = ttk.Treeview(parent, columns=cols, show="headings", style="Modern.Treeview")
        headers = {"class_name": "Classe", "level": "Niveau", "enrollment_count": "Inscrits"}
        for c in cols:
            self.top_tree.heading(c, text=headers[c], anchor='w')
            self.top_tree.column(c, width=180 if c != 'enrollment_count' else 120, anchor='w')
        self.top_tree.grid(row=0, column=0, sticky='nsew')
        yscroll = ttk.Scrollbar(parent, orient='vertical', command=self.top_tree.yview)
        self.top_tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky='ns')

        ttk.Button(parent, text="Exporter CSV", command=lambda: self._export_csv(self.top_tree, "top_classes.csv")).grid(row=1, column=0, sticky='e', pady=(6, 0))

    # ================= LOAD DATA =================
    def _load_overview(self):
        totals = query_all(
            """
            SELECT
                (SELECT COUNT(*) FROM students) AS students,
                (SELECT COUNT(*) FROM classes) AS classes,
                (SELECT COUNT(*) FROM attendance_sessions) AS sessions,
                (SELECT COUNT(*) FROM fee_invoices WHERE status='paid') AS payments_paid
            """
        )
        if totals:
            t = totals[0]
            self.kpi_vars['students'].set(str(t['students']))
            self.kpi_vars['classes'].set(str(t['classes']))
            self.kpi_vars['sessions'].set(str(t['sessions']))
            self.kpi_vars['payments_paid'].set(str(t['payments_paid']))

    def _apply_filters(self):
        self._reload_attendance()
        # sync overview charts to attendance date range
        self._render_charts()

    def _apply_filters_pay(self):
        self._reload_payments()
        # sync overview charts to payments date range
        self._render_charts(pay_tab=True)

    def _reload_attendance(self):
        # Clear
        for i in self.att_tree.get_children():
            self.att_tree.delete(i)
        start = self.start_input.get()
        end = self.end_input.get()
        sql = (
            """
            SELECT c.name AS class_name,
                   COUNT(ar.id) AS total_records,
                   SUM(CASE WHEN ar.status='Present' THEN 1 ELSE 0 END) AS Present,
                   SUM(CASE WHEN ar.status='Absent' THEN 1 ELSE 0 END) AS Absent,
                   SUM(CASE WHEN ar.status='Late' THEN 1 ELSE 0 END) AS Late,
                   SUM(CASE WHEN ar.status='Excused' THEN 1 ELSE 0 END) AS Excused
            FROM attendance_records ar
            JOIN attendance_sessions s ON s.id = ar.session_id
            JOIN classes c ON c.id = s.class_id
            WHERE date(s.session_date) BETWEEN date(?) AND date(?)
            GROUP BY c.id, c.name
            ORDER BY c.name
            """
        )
        rows = query_all(sql, (start, end))
        total = sum(r['total_records'] for r in rows) if rows else 0
        self.attendance_summary.configure(text=f"Total enregistrements: {total}")
        for r in rows:
            self.att_tree.insert("", "end", values=(r['class_name'], r['total_records'], r['Present'], r['Absent'], r['Late'], r['Excused']))

    def _reload_payments(self):
        for i in self.pay_tree.get_children():
            self.pay_tree.delete(i)
        start = self.start_input_pay.get()
        end = self.end_input_pay.get()
        sql = (
            """
            SELECT fi.status AS status,
                   COUNT(*) AS count,
                   ROUND(SUM(fi.amount_cents)/100.0, 2) AS total_amount
            FROM fee_invoices fi
            JOIN attendance_sessions s ON s.id = fi.session_id
            WHERE date(s.session_date) BETWEEN date(?) AND date(?)
            GROUP BY fi.status
            ORDER BY CASE fi.status WHEN 'paid' THEN 0 WHEN 'unpaid' THEN 1 ELSE 2 END
            """
        )
        rows = query_all(sql, (start, end))
        total_amount = sum(r['total_amount'] or 0 for r in rows) if rows else 0
        self.pay_summary.configure(text=f"Montant total: {total_amount} (toutes devises confondues)")
        for r in rows:
            self.pay_tree.insert("", "end", values=(r['status'], r['count'], r['total_amount']))

    def _reload_top_classes(self):
        for i in self.top_tree.get_children():
            self.top_tree.delete(i)
        sql = (
            """
            SELECT c.name AS class_name, c.level AS level, COUNT(ce.student_id) AS enrollment_count
            FROM classes c
            LEFT JOIN class_enrollments ce ON c.id = ce.class_id
            GROUP BY c.id, c.name, c.level
            ORDER BY enrollment_count DESC
            LIMIT 10
            """
        )
        rows = query_all(sql)
        for r in rows:
            self.top_tree.insert("", "end", values=(r['class_name'], r['level'], r['enrollment_count']))

    # ================= CHARTS =================
    def _render_charts(self, pay_tab: bool = False):
        """Render charts in the overview using current date range (attendance or payments tab)."""
        # Decide which date range to use
        if pay_tab:
            start, end = self.start_input_pay.get(), self.end_input_pay.get()
        else:
            start, end = (self.start_input.get() if self.start_input else date.today().strftime('%Y-%m-%d'),
                          self.end_input.get() if self.end_input else date.today().strftime('%Y-%m-%d'))

        # Fetch data
        pay = query_all(
            """
            SELECT fi.status AS status, COUNT(*) AS count
            FROM fee_invoices fi
            JOIN attendance_sessions s ON s.id = fi.session_id
            WHERE date(s.session_date) BETWEEN date(?) AND date(?)
            GROUP BY fi.status
            """,
            (start, end)
        )
        att = query_all(
            """
            SELECT ar.status AS status, COUNT(*) AS count
            FROM attendance_records ar
            JOIN attendance_sessions s ON s.id = ar.session_id
            WHERE date(s.session_date) BETWEEN date(?) AND date(?)
            GROUP BY ar.status
            """,
            (start, end)
        )

        # Clear old
        for w in self._chart_payment.winfo_children():
            w.destroy()
        for w in self._chart_attendance.winfo_children():
            w.destroy()

        ttk.Label(self._chart_payment, text=f"💳 Paiements par statut ({start} → {end})", style="CardTitle.TLabel").pack(anchor='w', padx=12, pady=(12, 0))
        ttk.Label(self._chart_attendance, text=f"📝 Assiduité par statut ({start} → {end})", style="CardTitle.TLabel").pack(anchor='w', padx=12, pady=(12, 0))

        if Figure is None or FigureCanvasTkAgg is None:
            # Fallback: simple textual summaries
            txt_pay = ", ".join([f"{r['status']}: {r['count']}" for r in pay]) or "Aucune donnée"
            txt_att = ", ".join([f"{r['status']}: {r['count']}" for r in att]) or "Aucune donnée"
            ttk.Label(self._chart_payment, text=txt_pay, style="Muted.TLabel").pack(anchor='w', padx=12, pady=8)
            ttk.Label(self._chart_attendance, text=txt_att, style="Muted.TLabel").pack(anchor='w', padx=12, pady=8)
            ttk.Label(self._chart_payment, text="Astuce: installez matplotlib pour voir des graphiques.", style="Muted.TLabel").pack(anchor='w', padx=12, pady=(0,12))
            ttk.Label(self._chart_attendance, text="Astuce: installez matplotlib pour voir des graphiques.", style="Muted.TLabel").pack(anchor='w', padx=12, pady=(0,12))
            return

        # Pie chart for payments
        fig1 = Figure(figsize=(4, 2.6), dpi=100)
        ax1 = fig1.add_subplot(111)
        labels = [r['status'] for r in pay]
        sizes = [r['count'] for r in pay]
        if not sizes:
            labels = ['aucun']
            sizes = [1]
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax1.axis('equal')
        canvas1 = FigureCanvasTkAgg(fig1, master=self._chart_payment)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=12)

        # Bar chart for attendance
        fig2 = Figure(figsize=(4, 2.6), dpi=100)
        ax2 = fig2.add_subplot(111)
        labels2 = [r['status'] for r in att]
        counts2 = [r['count'] for r in att]
        if not counts2:
            labels2 = ['aucun']
            counts2 = [0]
        ax2.bar(labels2, counts2, color=['#48bb78', '#f56565', '#ed8936', '#718096'][:len(labels2)])
        ax2.set_ylabel('Nombre')
        canvas2 = FigureCanvasTkAgg(fig2, master=self._chart_attendance)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=12)

    # ================= EXPORT =================
    def _export_csv(self, tree: ttk.Treeview, default_name: str):
        try:
            path = filedialog.asksaveasfilename(defaultextension='.csv', initialfile=default_name,
                                                filetypes=[('CSV Files', '*.csv')])
            if not path:
                return
            cols = tree['columns']
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                for item in tree.get_children():
                    values = tree.item(item, 'values')
                    writer.writerow(values)
            messagebox.showinfo("Export", f"Fichier exporté: {path}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))