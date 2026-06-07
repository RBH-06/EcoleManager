from tkinter import ttk
import tkinter as tk
import tkinter.font as tkfont

# Modern Web-Inspired Color Palette
PRIMARY = "#667eea"        # Beautiful purple-blue gradient start
PRIMARY_DARK = "#764ba2"   # Gradient end
PRIMARY_LIGHT = "#fdbdf5"  # Accent pink
SIDEBAR_BG = "#152259"     # Deep dark blue-gray
SIDEBAR_BG_GRADIENT = "#2d3748"  # Gradient overlay
SIDEBAR_BG_ACTIVE = "#4a5568"  # Active state
SIDEBAR_TEXT = "#cbd5e0"   # Light gray text  
SIDEBAR_TEXT_ACTIVE = "#ffffff"  # Pure white for active
HEADER_BG = "#ffffff"      # Clean white header
CONTENT_BG = "#aaadae"     # Very light gray background
CARD_BG = "#ffffff"
TEXT_COLOR = "#2d3748"     # Dark slate
MUTED_TEXT = "#718096"     # Muted gray
SUCCESS = "#48bb78"        # Green
WARNING = "#ed8936"        # Orange
DANGER = "#f56565"         # Red
ACCENT_BLUE = "#4299e1"    # Blue accent
ACCENT_PURPLE = "#9f7aea"  # Purple accent


def apply_dark_mode(is_dark: bool) -> None:
    global SIDEBAR_BG, SIDEBAR_BG_ACTIVE, SIDEBAR_TEXT, SIDEBAR_TEXT_ACTIVE, HEADER_BG, CONTENT_BG, CARD_BG, TEXT_COLOR, MUTED_TEXT
    if is_dark:
        SIDEBAR_BG = "#0f172a"
        SIDEBAR_BG_ACTIVE = "#1f2937"
        SIDEBAR_TEXT = "#e5e7eb"
        SIDEBAR_TEXT_ACTIVE = "#ffffff"
        HEADER_BG = "#0b1020"
        CONTENT_BG = "#0b1020"
        CARD_BG = "#111827"
        TEXT_COLOR = "#e5e7eb"
        MUTED_TEXT = "#9ca3af"
    else:
        # reset to defaults
        SIDEBAR_BG = "#1a1d29"
        SIDEBAR_BG_ACTIVE = "#4a5568"
        SIDEBAR_TEXT = "#cbd5e0"
        SIDEBAR_TEXT_ACTIVE = "#ffffff"
        HEADER_BG = "#ffffff"
        CONTENT_BG = "#f7fafc"
        CARD_BG = "#ffffff"
        TEXT_COLOR = "#2d3748"
        MUTED_TEXT = "#718096"


def setup_theme(root: tk.Tk) -> None:
    """Configure ttk styles for a clean, colorful, modern look (sans dépendances externes)."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Fonts (noms pour compatibilité)
    font_default = tkfont.Font(family="Segoe UI", size=10)
    font_title = tkfont.Font(family="Segoe UI", size=14, weight="bold")
    font_card_title = tkfont.Font(family="Segoe UI", size=12, weight="bold")
    font_small = tkfont.Font(family="Segoe UI", size=9)

    root.option_add("*Font", "{Segoe UI} 10")

    # Base
    root.configure(bg=CONTENT_BG)
    style.configure("TFrame", background=CONTENT_BG)
    style.configure("TLabel", background=CONTENT_BG, foreground=TEXT_COLOR)
    style.configure("TButton", padding=(12, 8))

    # Modern Header (clean white with subtle shadow)
    style.configure("Header.TFrame", background=HEADER_BG, relief="flat")
    style.configure("HeaderTitle.TLabel", background=HEADER_BG, foreground=TEXT_COLOR, font=font_title)
    style.configure("HeaderMuted.TLabel", background=HEADER_BG, foreground=MUTED_TEXT, font=font_small)
    style.configure("Header.TButton", background=HEADER_BG, foreground=TEXT_COLOR, padding=(16, 8))
    style.map("Header.TButton", 
              background=[("active", CONTENT_BG)],
              foreground=[("active", TEXT_COLOR)])

    # Modern Sidebar with gradient-like feel
    style.configure("Sidebar.TFrame", background=SIDEBAR_BG, relief="flat")
    
    # Sidebar brand/logo area
    style.configure("SidebarBrand.TLabel", 
                    background=SIDEBAR_BG, 
                    foreground=SIDEBAR_TEXT_ACTIVE, 
                    font=("Segoe UI", 16, "bold"),
                    padding=(20, 20))
    
    # Modern sidebar buttons with better spacing
    style.configure(
        "Sidebar.TButton",
        background=SIDEBAR_BG,
        foreground=SIDEBAR_TEXT,
        anchor="w",
        padding=(16, 12),
        relief="flat",
        borderwidth=0,
        focuscolor="none",
        font=("Segoe UI", 10)
    )
    style.map(
        "Sidebar.TButton",
        background=[("active", SIDEBAR_BG_ACTIVE), ("pressed", SIDEBAR_BG_ACTIVE)],
        foreground=[("active", SIDEBAR_TEXT_ACTIVE), ("pressed", SIDEBAR_TEXT_ACTIVE)],
    )

    # Hover style to emulate web nav hover
    style.configure(
        "SidebarHover.TButton",
        background="#2a3142",
        foreground=SIDEBAR_TEXT,
        anchor="w",
        padding=(16, 12),
        relief="flat",
        borderwidth=0,
        focuscolor="none",
        font=("Segoe UI", 10)
    )
    
    # Active/Selected sidebar button with accent
    style.configure(
        "SidebarSelected.TButton",
        background=SIDEBAR_BG_ACTIVE,
        foreground=SIDEBAR_TEXT_ACTIVE,
        anchor="w",
        padding=(16, 12),
        relief="flat",
        borderwidth=0,
        focuscolor="none",
        font=("Segoe UI", 10, "bold")
    )
    style.map(
        "SidebarSelected.TButton",
        background=[("active", PRIMARY), ("pressed", PRIMARY)],
        foreground=[("active", "#ffffff"), ("pressed", "#ffffff")],
    )

    # Modern Cards with subtle shadows
    style.configure("Card.TFrame", background=CARD_BG, relief="flat", borderwidth=0)
    style.configure("CardTitle.TLabel", background=CARD_BG, font=font_card_title, foreground=TEXT_COLOR)
    style.configure("Muted.TLabel", foreground=MUTED_TEXT, background=CARD_BG)
    
    # Special accent cards
    style.configure("CardAccent.TFrame", background=PRIMARY, relief="flat", borderwidth=0)
    style.configure("CardAccentTitle.TLabel", background=PRIMARY, font=font_card_title, foreground="#ffffff")
    style.configure("CardAccentMuted.TLabel", foreground="#e2e8f0", background=PRIMARY)

    # Modern Primary buttons with gradients
    style.configure("Primary.TButton", 
                   foreground="#FFFFFF", 
                   background=PRIMARY,
                   padding=(16, 10),
                   relief="flat",
                   borderwidth=0,
                   focuscolor="none",
                   font=("Segoe UI", 10, "bold"))
    style.map(
        "Primary.TButton",
        background=[("disabled", MUTED_TEXT), ("active", PRIMARY_DARK), ("pressed", PRIMARY_DARK), ("!disabled", PRIMARY)],
        foreground=[("!disabled", "#FFFFFF"), ("disabled", "#FFFFFF")],
    )
    
    # Secondary buttons
    style.configure("Secondary.TButton",
                   foreground=TEXT_COLOR,
                   background="#e2e8f0", 
                   padding=(16, 10),
                   relief="flat",
                   borderwidth=0,
                   focuscolor="none",
                   font=("Segoe UI", 10))
    style.map(
        "Secondary.TButton",
        background=[("active", "#cbd5e0"), ("pressed", "#cbd5e0")],
        foreground=[("active", TEXT_COLOR)],
    )

    # Treeview modern
    style.configure(
        "Modern.Treeview",
        background=CARD_BG,
        fieldbackground=CARD_BG,
        foreground=TEXT_COLOR,
        rowheight=28,
        borderwidth=0,
    )
    style.configure(
        "Modern.Treeview.Heading",
        background=CONTENT_BG,
        foreground=TEXT_COLOR,
        relief="flat",
        padding=6,
    )
    style.map("Modern.Treeview.Heading", background=[("active", PRIMARY_LIGHT)])

    # Modern Entry fields
    style.configure("Modern.TEntry", 
                   fieldbackground="#ffffff",
                   borderwidth=2,
                   relief="solid",
                   insertcolor=TEXT_COLOR,
                   selectbackground=PRIMARY_LIGHT,
                   selectforeground="#ffffff",
                   padding=(16, 12),
                   font=("Segoe UI", 11))
    style.map("Modern.TEntry",
             bordercolor=[("focus", PRIMARY), ("!focus", "#e2e8f0")],
             lightcolor=[("focus", PRIMARY), ("!focus", "#e2e8f0")],
             darkcolor=[("focus", PRIMARY), ("!focus", "#e2e8f0")])

    # Scrollbar minimal
    style.configure("Vertical.TScrollbar", gripcount=0, background=CONTENT_BG)