import os
import tkinter as tk
from tkinter import messagebox

from utils.config import APP_TITLE, load_settings
from db.connection import init_db
from db.seed import seed_initial_admin, seed_demo_data
from ui.login_window import LoginWindow
from utils.theme import setup_theme, apply_dark_mode
from utils.resources import get_resource_path


def main():
    # Initialize DB
    init_db()
    # Ensure default roles and admin user exist (admin/admin)
    try:
        seed_initial_admin()
    except Exception:
        pass

    # Seed demo data only if no classes or students exist yet
    # try:
    #     from db.connection import get_connection
    #     conn = get_connection()
    #     try:
    #         cur = conn.cursor()
    #         has_classes = cur.execute("SELECT 1 FROM classes LIMIT 1").fetchone() is not None
    #         has_students = cur.execute("SELECT 1 FROM students LIMIT 1").fetchone() is not None
    #     finally:
    #         conn.close()
    #     if not has_classes and not has_students:
    #         seed_demo_data()
    # except Exception:
    #     pass

    # Tkinter app root
    root = tk.Tk()
    root.title(APP_TITLE)

    # Set window icon during development
    try:
        icon_path = get_resource_path('src/assets/favicon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass
    
    # Make window responsive and modern
    root.state('zoomed')  # Start maximized on Windows
    root.minsize(1024, 768)  # Minimum size for proper functionality
    
    # Configure root for responsiveness
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    # Setup modern theme
    # Apply dark mode before creating styles, based on saved settings
    try:
        settings = load_settings()
        apply_dark_mode(settings.get("dark_mode", False))
    except Exception:
        pass
    setup_theme(root)

    app = LoginWindow(root)
    app.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()