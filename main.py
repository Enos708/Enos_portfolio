import flet as ft
import flet.canvas as cv
import os
import subprocess

try:
    import flet_video as fv
except ImportError:
    fv = None

# ── SHARED CONSTANTS ──────────────────────────────────────────────────────────
ACCENT_COLOR   = "#D7DEE2"
DIVIDER_COLOR  = "#7F8A8F"
IC_BADGE       = "#C9D1D6"
IC_BOOK        = "#9FB0B8"
IC_GROUPS      = "#B8C4C9"
IC_EMAIL       = "#D7DEE2"
IC_PHONE       = "#AAB6BB"
IC_INSTA       = "#C6CED2"
TEXT_COLOR     = ft.Colors.WHITE
SUBTLE_COLOR   = ft.Colors.with_opacity(0.76, ft.Colors.WHITE)
BG_COLOR       = "#111315"
CONCRETE_DARK  = "#17191A"
CONCRETE_MID   = "#2A2D2E"
CONCRETE_LIGHT = "#5A5F60"

HEADER_SIZE    = 28
SUBHEADER_SIZE = 20
CONTENT_SIZE   = 14
PROJECT_VIDEO_FILE = "MEKTEK_Video_Demo.mp4"

# ── CONSTELLATION BACKGROUND (built ONCE, reused every page) ──────────────────
def _build_background_shapes():
    shapes = []

    def paint(color, opacity=1.0, stroke_width=1.0, style=ft.PaintingStyle.FILL):
        return ft.Paint(
            color=ft.Colors.with_opacity(opacity, color),
            stroke_width=stroke_width,
            style=style,
        )

    # Concrete wall with uneven smoky patches.
    shapes.extend([
        cv.Oval(x=120, y=80, width=560, height=250, paint=paint(CONCRETE_LIGHT, 0.18)),
        cv.Oval(x=520, y=120, width=650, height=310, paint=paint("#727777", 0.13)),
        cv.Oval(x=1050, y=85, width=580, height=260, paint=paint("#666B6C", 0.12)),
        cv.Oval(x=1420, y=240, width=470, height=250, paint=paint("#0B0C0D", 0.22)),
        cv.Oval(x=-180, y=260, width=520, height=300, paint=paint("#08090A", 0.30)),
    ])

    # Subtle scratches and scuffs.
    for x1, y1, x2, y2, op in [
        (320, 185, 430, 220, 0.18), (470, 150, 620, 125, 0.12),
        (720, 260, 820, 210, 0.16), (940, 180, 1005, 290, 0.13),
        (1115, 105, 1245, 150, 0.10), (1320, 310, 1455, 280, 0.12),
        (220, 415, 345, 365, 0.12), (620, 430, 760, 390, 0.10),
        (1010, 385, 1160, 420, 0.11), (1500, 150, 1580, 245, 0.10),
    ]:
        shapes.append(cv.Line(
            x1=x1, y1=y1, x2=x2, y2=y2,
            paint=paint("#AEB4B6", op, 1.2, ft.PaintingStyle.STROKE),
        ))

    # Wall-floor seam and floor planks/perspective lines.
    shapes.extend([
        cv.Line(x1=0, y1=720, x2=1920, y2=720,
                paint=paint("#0B0C0D", 0.72, 4, ft.PaintingStyle.STROKE)),
        cv.Rect(x=0, y=722, width=1920, height=358, paint=paint("#0D0F10", 0.62)),
        cv.Rect(x=0, y=720, width=1920, height=38, paint=paint("#555A5B", 0.10)),
    ])

    for x in range(-140, 2040, 170):
        shapes.append(cv.Line(
            x1=x, y1=1080, x2=960 + (x - 960) * 0.32, y2=720,
            paint=paint("#7B8284", 0.11, 1.1, ft.PaintingStyle.STROKE),
        ))

    for y, op in [(790, 0.12), (860, 0.10), (935, 0.08), (1015, 0.07)]:
        shapes.append(cv.Line(
            x1=0, y1=y, x2=1920, y2=y,
            paint=paint("#7B8284", op, 1, ft.PaintingStyle.STROKE),
        ))

    # Dark edge vignette for readability.
    shapes.extend([
        cv.Rect(x=0, y=0, width=1920, height=1080, paint=paint("#050607", 0.18)),
        cv.Rect(x=0, y=0, width=1920, height=120, paint=paint("#050607", 0.22)),
        cv.Rect(x=0, y=930, width=1920, height=150, paint=paint("#050607", 0.35)),
        cv.Rect(x=0, y=0, width=170, height=1080, paint=paint("#050607", 0.18)),
        cv.Rect(x=1750, y=0, width=170, height=1080, paint=paint("#050607", 0.18)),
    ])
    return shapes

# Pre-compute once at import time — all pages share this
_BG_SHAPES = _build_background_shapes()


def build_background():
    return ft.Stack(
        controls=[
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1),
                    end=ft.Alignment(0, 1),
                    colors=["#0A0B0C", "#303435", "#1A1D1E", "#08090A"],
                    stops=[0.0, 0.32, 0.68, 1.0],
                ),
            ),
            ft.Container(expand=True, bgcolor=ft.Colors.with_opacity(0.16, "#000000")),
            cv.Canvas(expand=True, shapes=_BG_SHAPES),
        ],
        expand=True,
    )


# ── TOP NAV ───────────────────────────────────────────────────────────────────
def build_top_nav(page: ft.Page, active_key: str):
    def go(route):
        def handler(e):
            page.go(route)
        return handler

    def nav_button(label, icon, route):
        is_active = active_key == route.strip("/")
        return ft.TextButton(
            content=ft.Row(
                [
                    ft.Icon(icon, size=15,
                            color=TEXT_COLOR if is_active else ACCENT_COLOR),
                    ft.Text(label, size=13, weight=ft.FontWeight.W_500,
                            color=TEXT_COLOR if is_active else ACCENT_COLOR),
                ],
                spacing=5,
                tight=True,
            ),
            on_click=go(route),
            style=ft.ButtonStyle(
                padding=ft.Padding(10, 6, 10, 6),
                bgcolor=ft.Colors.with_opacity(0.12, ACCENT_COLOR) if is_active
                        else ft.Colors.TRANSPARENT,
                overlay_color=ft.Colors.with_opacity(0.08, ACCENT_COLOR),
            ),
        )

    return ft.Container(
        bgcolor=ft.Colors.with_opacity(0.95, BG_COLOR),
        # ── taller navbar ──
        padding=ft.Padding(20, 14, 20, 14),
        border=ft.border.Border(
            bottom=ft.border.BorderSide(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE))
        ),
        content=ft.Row(
            controls=[
                # ── UNAM logo replacing text ──
                ft.TextButton(
                    content=ft.Row([
                        ft.Image(
                            src="unam_logo.png",
                            width=70, height=70,
                            fit=ft.BoxFit.CONTAIN,
                            error_content=ft.Text(
                                "UNAM", size=22,
                                weight=ft.FontWeight.BOLD,
                                color=ACCENT_COLOR,
                            ),
                        ),
                        ft.Column([
                            ft.Text("Moses Enos P", size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE),
                            ft.Text("Computer Programming I · 2026",
                                    size=10, color=SUBTLE_COLOR),
                        ], spacing=1, tight=True),
                    ], spacing=10, tight=True),
                    on_click=go("/home"),
                    style=ft.ButtonStyle(overlay_color=ft.Colors.TRANSPARENT),
                ),
                ft.Row(
                    controls=[
                        nav_button("Home",       ft.Icons.HOME,        "/home"),
                        nav_button("Timeline",   ft.Icons.TIMELINE,    "/timeline"),
                        nav_button("GitHub",     ft.Icons.CODE,        "/github"),
                        nav_button("MATLAB Hub", ft.Icons.SCHOOL,      "/matlab"),
                        nav_button("Blog",       ft.Icons.ARTICLE,     "/blog"),
                        nav_button("Contact",    ft.Icons.MAIL,        "/contact"),
                    ],
                    spacing=4,
                    alignment=ft.MainAxisAlignment.END,
                    wrap=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


# ── FULL-PAGE SHELL ───────────────────────────────────────────────────────────
def page_shell(page: ft.Page, active_key: str, body: ft.Control):
    nav = build_top_nav(page, active_key)
    scrollable = ft.Column(
        controls=[
            ft.Container(content=body, padding=ft.Padding(30, 30, 30, 40), expand=True)
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
    page_col = ft.Column(
        controls=[nav, scrollable],
        expand=True,
        spacing=0,
    )
    return ft.Stack(
        controls=[build_background(), page_col],
        expand=True,
    )


# ── HELPER WIDGETS ────────────────────────────────────────────────────────────
def math_module_card(title, description, top_formula,
                     bottom_formula=None, plain_suffix=""):
    formula_controls = []
    if bottom_formula:
        formula_controls += [
            ft.Text(top_formula, size=14, color="#F1D19C",
                    weight=ft.FontWeight.BOLD),
            ft.Container(width=160, height=1, bgcolor=DIVIDER_COLOR,
                         margin=ft.Margin(top=2, bottom=2)),
            ft.Text(bottom_formula, size=14, color="#F1D19C",
                    weight=ft.FontWeight.BOLD),
        ]
    else:
        formula_controls.append(
            ft.Text(top_formula, size=14, color="#F1D19C", italic=True)
        )
    if plain_suffix:
        formula_controls.append(
            ft.Text(plain_suffix, size=12, color=SUBTLE_COLOR)
        )

    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ACCENT_COLOR),
            ft.Text(description, size=CONTENT_SIZE, color=TEXT_COLOR),
            ft.Container(
                content=ft.Column(
                    formula_controls,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=12,
                bgcolor=ft.Colors.with_opacity(0.15, BG_COLOR),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.10, ft.Colors.WHITE)),
                border_radius=6,
            ),
        ], spacing=10),
        padding=20,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
        border_radius=10,
        col={"sm": 12, "md": 6, "lg": 4},
    )


def blog_post_preview(title, description):
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=SUBHEADER_SIZE,
                    weight=ft.FontWeight.BOLD, color=ACCENT_COLOR),
            ft.Text(description, size=CONTENT_SIZE, color=TEXT_COLOR),
            ft.TextButton("Read full post…",
                          style=ft.ButtonStyle(color=ACCENT_COLOR)),
        ], spacing=5),
        margin=ft.Margin(bottom=20),
        padding=15,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
        border_radius=10,
    )


def blog_article_card(title, concept, explanation, formula=None):
    controls = [
        ft.Text(title, size=SUBHEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=ACCENT_COLOR),
        ft.Text(concept, size=13, color=ft.Colors.with_opacity(0.86, ft.Colors.WHITE),
                weight=ft.FontWeight.W_600),
        ft.Text(explanation, size=CONTENT_SIZE, color=TEXT_COLOR),
    ]

    if formula:
        controls.append(
            ft.Container(
                content=ft.Text(formula, size=15, color="#FFE1A3",
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER),
                padding=14,
                bgcolor=ft.Colors.with_opacity(0.14, ACCENT_COLOR),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.22, ACCENT_COLOR)),
                border_radius=8,
            )
        )

    return ft.Container(
        content=ft.Column(controls, spacing=10),
        margin=ft.Margin(bottom=20),
        padding=18,
        bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
        border_radius=10,
    )


def cert_card(img_path):
    return ft.Container(
        content=ft.Image(src=img_path, border_radius=10, fit=ft.BoxFit.COVER),
        padding=10,
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10,
                            color=ft.Colors.with_opacity(0.26, ft.Colors.BLACK)),
        col={"sm": 12, "md": 6},
    )


def skill_chip(label, icon, color):
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=16, color=color),
            ft.Text(label, size=13, color=ft.Colors.WHITE,
                    weight=ft.FontWeight.W_500),
        ], spacing=6, tight=True),
        padding=ft.Padding(12, 8, 12, 8),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.25, color)),
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.08, color),
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE BODIES
# ══════════════════════════════════════════════════════════════════════════════

# ── HOME ──────────────────────────────────────────────────────────────────────
def home_body():
    profile_section = ft.ResponsiveRow(
        controls=[
            ft.Container(
                col={"sm": 12, "md": 5},
                content=ft.Container(
                    width=280, height=420,
                    border_radius=20,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.3, ACCENT_COLOR)),
                    padding=10,
                    content=ft.Image(src="Enos.jpeg", fit=ft.BoxFit.COVER,
                                     border_radius=14),
                ),
            ),
            ft.Container(
                col={"sm": 12, "md": 7},
                padding=ft.Padding(left=15, right=15, top=10, bottom=10),
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Text("Moses Enos P", size=36,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE),
                            ft.Text("Civil Engineering Student | Lead Developer",
                                    size=16, color=ACCENT_COLOR,
                                    weight=ft.FontWeight.W_500),
                        ]),
                        ft.Divider(color=DIVIDER_COLOR, height=10, thickness=1),
                        ft.Column(spacing=8, controls=[
                            ft.Text("Project Brief", size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE),
                            ft.Text(
                                "Serving as the Lead Developer for Group 15 in the "
                                "Mobile App Development For Computer Programming I, "
                                "I manage the software implementation lifecycle for "
                                "MechTek—our cross-platform Machine Fault Reporting "
                                "System built using Expo, React Native, and Firebase.",
                                size=15, color=SUBTLE_COLOR,
                            ),
                        ]),
                        ft.Column(spacing=5, controls=[
                            ft.Row([
                                ft.Icon(ft.Icons.BADGE, color=IC_BADGE, size=16),
                                ft.Text("Student Number: 225150395",
                                        size=14, color=SUBTLE_COLOR),
                            ]),
                            ft.Row([
                                ft.Icon(ft.Icons.BOOK_ROUNDED, color=IC_BOOK, size=16),
                                ft.Text("Module: Computer Programming I",
                                        size=14, color=SUBTLE_COLOR),
                            ]),
                            ft.Row([
                                ft.Icon(ft.Icons.GROUPS_3, color=IC_GROUPS, size=16),
                                ft.Text("Assigned Team: Group 15 (MechTek)",
                                        size=14, color=SUBTLE_COLOR),
                            ]),
                        ]),
                    ],
                ),
            ),
            
        ],
        spacing=30,
        run_spacing=30,
    )

    # ── SKILLS & TECH SECTION (the area indicated in the image) ──
    skills_section = ft.Container(
        margin=ft.Margin(top=40, bottom=0, left=0, right=0),
        content=ft.Column([
            ft.Row([
                ft.Container(
                    width=4, height=30, bgcolor=ACCENT_COLOR,
                    border_radius=2,
                    margin=ft.Margin(right=12, top=0, left=0, bottom=0),
                ),
                ft.Text("Skills & Technologies",
                        size=SUBHEADER_SIZE + 2,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=6),
            ft.Text(
                "A snapshot of the tools, frameworks, and languages I apply across "
                "the MechTek project and my academic coursework at UNAM.",
                size=CONTENT_SIZE, color=SUBTLE_COLOR,
            ),
            ft.Container(height=18),

            # Row 1 — Languages
            ft.Text("Languages", size=13, color=ACCENT_COLOR,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=6),
            ft.Row(wrap=True, spacing=10, run_spacing=10, controls=[
                skill_chip("Python",      ft.Icons.CODE,            "#5BC8F5"),
                skill_chip("JavaScript",  ft.Icons.JAVASCRIPT,      "#FACC15"),
                skill_chip("JSX / React", ft.Icons.WIDGETS,         "#A78BFA"),
                skill_chip("MATLAB",      ft.Icons.CALCULATE,       "#4ADE80"),
            ]),
            ft.Container(height=16),

            # Row 2 — Frameworks & Tools
            ft.Text("Frameworks & Tools", size=13, color=ACCENT_COLOR,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=6),
            ft.Row(wrap=True, spacing=10, run_spacing=10, controls=[
                skill_chip("Flet",          ft.Icons.DESKTOP_WINDOWS, "#5BC8F5"),
                skill_chip("React Native",  ft.Icons.PHONE_ANDROID,   "#F472B6"),
                skill_chip("Expo",          ft.Icons.ROCKET_LAUNCH,   "#FB923C"),
                skill_chip("Firebase",      ft.Icons.LOCAL_FIRE_DEPARTMENT, "#FACC15"),
                skill_chip("AsyncStorage",  ft.Icons.CLOUD_SYNC,      "#34D399"),
                skill_chip("Git & GitHub",  ft.Icons.MERGE_TYPE,      "#F87171"),
            ]),
            ft.Container(height=16),

            # Row 3 — Engineering domains
            ft.Text("Engineering Domains", size=13, color=ACCENT_COLOR,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=6),
            ft.Row(wrap=True, spacing=10, run_spacing=10, controls=[
                skill_chip("Civil Engineering",        ft.Icons.DOMAIN,          "#A78BFA"),
                skill_chip("Asset Fault Tracking",     ft.Icons.BUILD_CIRCLE,    "#4ADE80"),
                skill_chip("NoSQL / Firestore",        ft.Icons.STORAGE,         "#5BC8F5"),
                skill_chip("System Architecture",      ft.Icons.ACCOUNT_TREE,    "#FB923C"),
                skill_chip("Cross-Platform Dev",       ft.Icons.DEVICES,         "#F472B6"),
            ]),

            ft.Container(height=30),
            ft.Divider(color=DIVIDER_COLOR, thickness=1),

            # Quick-stats bar
            ft.Container(height=10),
        ]),
        padding=ft.Padding(30, 28, 30, 28),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
        border_radius=14,
        bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
    )

    return ft.Column(
        expand=True,
        controls=[
            profile_section, 
            skills_section,
            ft.Container(expand=True),
            ft.Divider(color=DIVIDER_COLOR, height=60),
            ft.Column(
                [
                    ft.Text(
                        "© 2026 Enos Moses | Mobile App Development For Computer Programming ",
                        color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                        size=12, italic=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                width=float("inf"),
            ),
            ft.Container(height=20),
        ], 
        spacing=0
    )



def _stat_card(value, label, icon, color):
    return ft.Container(
        col={"xs": 6, "sm": 6, "md": 3},
        content=ft.Column([
            ft.Icon(icon, size=28, color=color),
            ft.Text(value, size=32, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Text(label, size=12, color=SUBTLE_COLOR,
                    text_align=ft.TextAlign.CENTER),
        ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=20,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.15, color)),
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.07, color),
    )


# ── TIMELINE ─────────────────────────────────────────────────────────────────
def timeline_body():
    entries = [
        ("Weeks 1–2: Initiation & Architecture",
         "Conducted initial design meetings to finalize the SRS technical contracts, "
         "role-based access flows, and data boundaries.",
         ft.Icons.ASSIGNMENT_TURNED_IN, "#5BC8F5", "SRS ARCHITECTURE"),
        ("Weeks 3–5: UI/UX & Frontend Scaffolding",
         "Collaborated with design leads to engineer modular components, form handling "
         "states, and responsive view containers matching mobile dimensions.",
         ft.Icons.DASHBOARD_CUSTOMIZE, "#A78BFA", "UI COMPONENTS"),
        ("Weeks 6–8: Core Route & Navigation Engineering",
         "Constructed state routing arrays, layout switching flows, and contextual "
         "tracking views for workers, technicians, and supervisors.",
         ft.Icons.ALT_ROUTE, "#4ADE80", "ROUTING MATRIX"),
        ("Weeks 9–10: Optimization & Offline Queue Strategy",
         "Configured system performance parameters, component rendering optimizations, "
         "and AsyncStorage local data fallback setups.",
         ft.Icons.CLOUD_SYNC, "#FB923C", "ASYNC STORAGE"),
        ("Weeks 11–12+: Deployment & Quality Assurance",
         "Assisted with end-to-end connectivity verification, Firestore document rule "
         "testing, and production behavior QA against SRS system benchmarks.",
         ft.Icons.VERIFIED, "#F472B6", "PRODUCTION QA"),
    ]

    cards = [
        ft.Container(
            padding=20,
            margin=ft.Margin(bottom=15, top=0, left=0, right=0),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        content=ft.Icon(icon_node, color=node_color, size=24),
                        margin=ft.Margin(right=10, top=2, left=0, bottom=0),
                    ),
                    ft.Column(expand=True, spacing=8, controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(title, size=18,
                                        weight=ft.FontWeight.BOLD, color=ACCENT_COLOR),
                                ft.Container(
                                    content=ft.Text(badge_text, size=11,
                                                    color=ft.Colors.WHITE,
                                                    weight=ft.FontWeight.W_600),
                                    bgcolor=ft.Colors.with_opacity(0.15, ACCENT_COLOR),
                                    padding=10, border_radius=15,
                                ),
                            ],
                        ),
                        ft.Text(desc, size=CONTENT_SIZE, color=SUBTLE_COLOR),
                    ]),
                ],
            ),
        )
        
        for title, desc, icon_node, node_color, badge_text in entries
    ]

    return ft.Column(controls=[
        ft.Text("Project Timeline", size=HEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(
            content=ft.Text(
                "As the Lead Developer of Group 15, I spearheaded the technical "
                "development of MechTek. My primary responsibility involved constructing "
                "system architecture boundaries, implementing secure front-to-back "
                "workflows with Firebase, and turning core SRS functional specifications "
                "into cross-platform code modules.",
                size=CONTENT_SIZE, color=SUBTLE_COLOR,
            ),
            margin=ft.Margin(bottom=25, top=10),
        ),
        
        *cards,
        ft.Divider(color=DIVIDER_COLOR, height=60),
        ft.Column(
            [
                ft.Text(
                    "© 2026 Enos Moses | Mobile App Development For Computer Programming ",
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                    size=12, italic=True,
                    text_align=ft.TextAlign.CENTER, # Ensures multi-line text wraps centered
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=float("inf"), # Forces the alignment container to span the full window width
        ),
        ft.Container(height=20),

    ], spacing=0)


# ── GITHUB ────────────────────────────────────────────────────────────────────
def github_body():
    return ft.Column(controls=[
        ft.Text("GitHub Evidence & Documentation", size=HEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(
            content=ft.Text(
                "Working alongside our GitHub Managers, I pushed structural baseline "
                "revisions, engineered major routing blocks, and resolved script merge "
                "constraints. Our workflow utilised descriptive branching schemas to "
                "track functional progress dynamically against academic criteria.",
                size=CONTENT_SIZE, color=SUBTLE_COLOR,
            ),
            margin=ft.Margin(bottom=20, top=10),
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Mining Engineering Module Impact Summary",
                        size=SUBHEADER_SIZE, weight=ft.FontWeight.BOLD,
                        color=ACCENT_COLOR),
                ft.Text(
                    "Problem Statement: The structural asset registries for Mining "
                    "infrastructure facilities were suffering transaction synchronization "
                    "blockages over standard network connections.\n\n"
                    "Individual Resolution: I engineered a local asynchronous payload "
                    "boundary buffer utilising AsyncStorage. By capturing system faults "
                    "instantly at the device line, structural engineers can report asset "
                    "distress metrics without active cell signals, ensuring zero record "
                    "dropouts across mining operations.",
                    size=CONTENT_SIZE, color=TEXT_COLOR,
                ),
            ]),
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
            border_radius=10,
            margin=ft.Margin(bottom=20),
        ),
        ft.Divider(height=10, thickness=1,
                   color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
        ft.Text("Project Repository", size=SUBHEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(
            content=ft.ElevatedButton(
                "View Production Repository on GitHub",
                icon=ft.Icons.CODE,
                style=ft.ButtonStyle(
                    color=ft.Colors.BLACK, bgcolor=ACCENT_COLOR,
                    padding=20,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                url="https://github.com/224032909/MechTek.git",
            ),
            padding=ft.Padding(left=40, right=40),
        ),
        ft.Container(height=20),
        ft.Text("Verifiable Pull Request & Code Review Logs",
                size=SUBHEADER_SIZE, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.ResponsiveRow([
            ft.Container(
                content=ft.Column(controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.CALL_MERGE, color="green"),
                        title=ft.Text("PR #12: Local Async Storage Layer",
                                      color=ft.Colors.WHITE,
                                      weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(
                            "Merged 'feature/async-storage' into main",
                            color=ACCENT_COLOR),
                    ),
                    ft.Container(
                        content=ft.Image(src="github_contr.png",
                                         border_radius=4, fit=ft.BoxFit.COVER),
                        padding=ft.Padding(left=16, right=16, bottom=16),
                    ),
                ], spacing=0),
                col={"sm": 12, "md": 6},
                bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
                border_radius=8,
            ),
            ft.Container(
                content=ft.Column(controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.RATE_REVIEW, color="amber"),
                        title=ft.Text("Feature: Report Fault Screen Layout",
                                      color=ft.Colors.WHITE,
                                      weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(
                            "Fixed formatting in ReportFaultScreen.jsx",
                            color=ACCENT_COLOR),
                    ),
                    ft.Container(
                        content=ft.Image(src="report.png", height=200,
                                         border_radius=4, fit=ft.BoxFit.COVER),
                        padding=ft.Padding(left=16, right=16, bottom=16),
                    ),
                ], spacing=0),
                col={"sm": 12, "md": 6},
                bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
                border_radius=8,
            ),
        ], spacing=15),
        ft.Container(height=15),
        ft.Container(
            content=ft.Column(controls=[
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HISTORY, color="blue"),
                    title=ft.Text("Development Commit History Screenshots",
                                  color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(
                        "Chronological stream of verified code repository updates",
                        color=ACCENT_COLOR),
                ),
                ft.Container(
                    content=ft.Image(src="history.png",
                                     border_radius=4, fit=ft.BoxFit.COVER),
                    padding=ft.Padding(left=16, right=16, bottom=16),
                ),
            ], spacing=0),
            bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
            border_radius=8,
        ),
        ft.Divider(color=DIVIDER_COLOR, height=60),
        ft.Column(
            [
                ft.Text(
                    "© 2026 Enos Moses | Mobile App Development For Computer Programming ",
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                    size=12, italic=True,
                    text_align=ft.TextAlign.CENTER, # Ensures multi-line text wraps centered
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=float("inf"), # Forces the alignment container to span the full window width
        ),
        ft.Container(height=20),

    ], spacing=10)


# ── MATLAB ────────────────────────────────────────────────────────────────────
def matlab_body():
    images = [
        "matlab1.png", "matlab2.png", "matlab3.png", "matlab4.png",
        "matlab5.png", "matlab6.png", "matlab7.png", "matlab8.png",
    ]
    labels = {
        "matlab1.png": "Calculations with Vectors and Matrices",
        "matlab2.png": "Make and Manipulate Matrices",
        "matlab3.png": "MATLAB Onramp",
        "matlab4.png": "Simulink Onramp",
        "matlab5.png": "Analyzing Results in Simulink",
        "matlab6.png": "Semi-Automated Image Segmentation",
        "matlab7.png": "Create Animated Plots with MATLAB",
        "matlab8.png": "Simulink Fundamentals",
    }

    return ft.Column(controls=[
        ft.Text("MATLAB Academic Hub", size=HEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(
            content=ft.Text(
                "Verified course completions from the MathWorks Learning Center. "
                "All 8 self-paced certificates were earned as part of the Computer "
                "Programming I module requirements for Semester 1, 2026.",
                size=CONTENT_SIZE, color=SUBTLE_COLOR,
            ),
            margin=ft.Margin(bottom=20, top=10),
        ),
        ft.ResponsiveRow(
            controls=[
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 3},
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            cert_card(img),
                            ft.Text(labels.get(img, "MATLAB Course"),
                                    size=14, weight=ft.FontWeight.W_500,
                                    color=ft.Colors.WHITE,
                                    text_align=ft.TextAlign.CENTER),
                        ],
                    ),
                )
                for img in images
            ],
            spacing=10, run_spacing=20,
        ),
        ft.Divider(color=DIVIDER_COLOR, height=60),
        ft.Column(
            [
                ft.Text(
                    "© 2026 Enos Moses | Mobile App Development For Computer Programming ",
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                    size=12, italic=True,
                    text_align=ft.TextAlign.CENTER, # Ensures multi-line text wraps centered
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=float("inf"), # Forces the alignment container to span the full window width
        ),
        ft.Container(height=20),

    ])




# ── BLOG ──────────────────────────────────────────────────────────────────────
def project_video_player():
    if fv is None:
        return ft.Container(
            height=260,
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ACCENT_COLOR)),
            bgcolor=ft.Colors.with_opacity(0.06, TEXT_COLOR),
            alignment=ft.Alignment(0.0, 0.0),
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.VIDEOCAM_OFF_ROUNDED, size=44, color=ACCENT_COLOR),
                    ft.Text("Video player package missing", color=TEXT_COLOR, weight="bold"),
                    ft.Text(
                        "Run: python -m pip install flet-video",
                        color=ft.Colors.with_opacity(0.65, TEXT_COLOR),
                        size=12,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
        )

    return ft.Container(
        height=300,
        border_radius=10,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        bgcolor=BG_COLOR,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ACCENT_COLOR)),
        content=fv.Video(
            playlist=[fv.VideoMedia(PROJECT_VIDEO_FILE)],
            title="MechTek Demo Video",
            aspect_ratio=16 / 9,
            fit=ft.BoxFit.CONTAIN,
            fill_color=BG_COLOR,
            autoplay=False,
            muted=False,
            volume=100,
            filter_quality=ft.FilterQuality.HIGH,
            expand=True,
        ),
    )


def blog_body():
    return ft.Column(controls=[
        ft.Text("Technical Blog: Confidence in Concepts", size=HEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(
            content=ft.Text(
                "This section documents my individual Lead Developer contribution "
                "to MechTek. My assigned responsibility was converting the SRS into "
                "working technical flows: role-based access, fault reporting, "
                "Firestore data boundaries, offline reliability, and engineering "
                "metrics for industrial maintenance decisions.",
                size=CONTENT_SIZE, color=SUBTLE_COLOR,
            ),
            margin=ft.Margin(bottom=30, top=10),
        ),
        blog_article_card(
            "1. Translating the SRS into App Architecture",
            "Concept: requirements traceability and modular route design",
            "As Lead Developer, I used the SRS as the technical contract for the "
            "MechTek application. The system had to support workers, technicians, "
            "and supervisors, so the code structure needed clear role boundaries. "
            "My work focused on turning the required workflow into screens and "
            "navigation paths: a worker reports a fault, the supervisor assigns it, "
            "and the technician updates the repair status. This reduces confusion "
            "in a large team because each screen maps back to a specific requirement "
            "instead of being built as an isolated interface.",
            "Route Access = User Role -> Allowed Dashboard + Allowed Actions",
        ),
        blog_article_card(
            "2. Firestore Data Boundaries for Fault Reporting",
            "Concept: NoSQL collections, access patterns, and real-time sync",
            "The SRS defines three important Firestore areas: users, machines, and "
            "faults. My contribution as Lead Developer was to reason about how the "
            "frontend should read and write those records without mixing user "
            "responsibilities. Workers should create and track their own faults, "
            "technicians should update assigned repairs, and supervisors should see "
            "the full operational picture. This structure protects accountability "
            "because every status change belongs to a user role and a timestamped "
            "fault record.",
            "Fault Record = Machine ID + Reporter ID + Status + Media URLs + Timestamp",
        ),
        blog_article_card(
            "3. Offline Reliability in Mining and Heavy Industry",
            "Concept: local persistence and queued synchronization",
            "The SRS states that MechTek must support offline operation because "
            "industrial sites can have weak or unstable connectivity. My Lead "
            "Developer focus was making the fault workflow resilient: if a user "
            "creates a report while offline, the app should preserve the payload "
            "locally and sync it once the connection returns. This matters in mining "
            "and maintenance environments because a lost report can delay repairs, "
            "increase downtime, and remove the audit trail needed by supervisors.",
            "Queued Faults = Offline Submissions - Successfully Synced Submissions",
        ),
        blog_article_card(
            "4. Measuring Maintenance Impact with Programming Logic",
            "Concept: using mathematical notation to explain system analytics",
            "The supervisor dashboard is not only a list of faults; it should help "
            "the engineering team understand repair performance. The key metric is "
            "Mean Time To Repair, which compares the time a fault was reported with "
            "the time it was fixed. In programming terms, each fixed fault contributes "
            "one repair duration, and the dashboard can average those durations to "
            "show whether the maintenance process is improving.",
            "MTTR = [∑ⁿᵢ₌₁ (Fixed Timeᵢ - Reported Timeᵢ)] / N",
        ),
        blog_article_card(
            "5. Cost Awareness in Engineering Decisions",
            "Concept: linking software records to operational cost reasoning",
            "MechTek supports better maintenance decisions by recording which "
            "machines fail, how often they fail, and how long repairs take. When "
            "materials or parts are involved, the same records can support a basic "
            "cost model. This helps connect programming work to engineering impact: "
            "software does not only store reports, it produces evidence for planning "
            "maintenance resources.",
            "Total Cost = ∑ⁿᵢ₌₁ (Qᵢ × Pᵢ) + Overheads",
        ),

# ── VIDEO RESOURCE SECTION ─────────────────────────────────────────────
        ft.Container(
            padding=ft.Padding.symmetric(vertical=10),
            content=ft.Divider(height=1, color=ft.Colors.with_opacity(0.08, TEXT_COLOR))
        ),
        ft.Text("Contribution Video",
                size=SUBHEADER_SIZE, weight=ft.FontWeight.W_700, color=TEXT_COLOR),
        ft.Container(
            padding=24,
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.05, TEXT_COLOR),
            content=ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 4},
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Text("VIDEO RESOURCE", size=10, weight="bold", color=ACCENT_COLOR),
                                    bgcolor=ft.Colors.with_opacity(0.2, ACCENT_COLOR),
                                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=20,
                                ),
                                ft.Text("Play MechTek Demo Video", color=TEXT_COLOR, size=20, weight="bold"),
                                ft.Text(
                                    "Watch my project contribution video directly inside this portfolio.",
                                    color=ft.Colors.with_opacity(0.6, TEXT_COLOR), size=13,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            spacing=8,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 8},
                        content=project_video_player(),
                    ),
                ],
                spacing=18,
                run_spacing=18,
            ),
        ),
        # ── END VIDEO RESOURCE SECTION ─────────────────────────────────────────
        ft.Text("System Mathematics Summary",
                size=SUBHEADER_SIZE, weight=ft.FontWeight.W_700, color=TEXT_COLOR),

        ft.ResponsiveRow(
            [
                math_module_card(
                    "Fault Lifecycle Workflow",
                    "Digitization and systematic progression tracking of industrial asset breakdowns.",
                    "Status Lifecycle: Reported -> Repairing -> Fixed",
                ),
                math_module_card(
                    "Mean Time To Repair (MTTR)",
                    "Firestore timestamps can be used to measure repair turnaround across fixed faults.",
                    "MTTR = [ sum(n, i=1) (Maintenance_Time_i) ] / N",
                    "N = Total Number of Fixed Assets",
                    "Notation Compliant Formula Model",
                ),
                math_module_card(
                    "Asset Status Indexing",
                    "Machine records map operational condition to the correct role-based workflow.",
                    "Condition Mapping: Active || Faulty || Under_Repair",
                ),
                math_module_card(
                    "Operational Financial Model",
                    "A basic cost model connects quantities, unit prices, and overheads to maintenance planning.",
                    "Total Cost = sum(n, i=1) (Q_i x P_i) + Overheads",
                    None,
                    "Aggregate Procurement Value Contract",
                ),
            ],
            spacing=24,
            run_spacing=24,
        ),

        ft.Divider(color=DIVIDER_COLOR, height=60),
        ft.Column(
            [
                ft.Text(
                    "© 2026 Enos Moses | Mobile App Development For Computer Programming",
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                    size=12, italic=True,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=float("inf"),
        ),
        ft.Container(height=20),
    ])


# ── CONTACT ───────────────────────────────────────────────────────────────────
def contact_body(page: ft.Page):
    name_field  = ft.TextField(label="Name",    border_color=ft.Colors.WHITE,
                                color=ft.Colors.WHITE, cursor_color=ft.Colors.WHITE)
    email_field = ft.TextField(label="Email",   border_color=ft.Colors.WHITE,
                                color=ft.Colors.WHITE)
    msg_field   = ft.TextField(label="Message", multiline=True, min_lines=3,
                                border_color=ft.Colors.WHITE, color=ft.Colors.WHITE)

    return ft.Column(controls=[
        ft.Text("Contact Me", size=32, weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE),
        ft.Container(
            padding=20,
            content=ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        col={"sm": 12, "md": 6},
                        padding=20,
                        content=ft.Column([
                            ft.Text(
                                "I am always open to new academic collaborations, "
                                "development opportunities, or discussions surrounding "
                                "industrial asset tracking and civil system structures. "
                                "Drop me a message below to connect!",
                                size=16, color=ft.Colors.WHITE,
                                text_align=ft.TextAlign.LEFT,
                            ),
                            ft.Container(height=15),
                            ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.EMAIL, color=ACCENT_COLOR, size=18),
                                    ft.Text("Email: ", weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE, size=15),
                                    ft.Text("enospanduleni@gmail.com",
                                            color=SUBTLE_COLOR, size=15),
                                ], spacing=5),
                                ft.Row([
                                    ft.Icon(ft.Icons.PHONE, color=ACCENT_COLOR, size=18),
                                    ft.Text("Cell: ", weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE, size=15),
                                    ft.Text("+264 81 848 9142",
                                            color=SUBTLE_COLOR, size=15),
                                ], spacing=5),
                                ft.Row([
                                    ft.Icon(ft.Icons.CAMERA_ALT, color=ACCENT_COLOR, size=18),
                                    ft.Text("Instagram: ", weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE, size=15),
                                    ft.Text("e_n_o_s_rna",
                                            color=SUBTLE_COLOR, size=15),
                                ], spacing=5),
                            ], spacing=10),
                        ])
                    ),
                    ft.Container(
                        col={"sm": 12, "md": 5},
                        padding=30,
                        bgcolor=ft.Colors.with_opacity(0.12, ACCENT_COLOR),
                        border=ft.Border.all(
                            1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
                        border_radius=20,
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                name_field, email_field, msg_field,
                                ft.ElevatedButton(
                                    "Send Message",
                                    style=ft.ButtonStyle(bgcolor=DIVIDER_COLOR,
                                                         color=ft.Colors.WHITE),
                                    width=float("inf"),
                                    on_click=lambda _: page.launch_url(
                                        f"mailto:enospanduleni@gmail.com"
                                        f"?subject=Message from {name_field.value}"
                                        f"&body=From: {email_field.value}"
                                        f"%0D%0A%0D%0A{msg_field.value}"
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ),
        ft.Divider(color=DIVIDER_COLOR, height=60),
        ft.Column(
            [
                ft.Text(
                    "© 2026 Enos Moses | Mobile App Development For Computer Programming",
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                    size=12, italic=True,
                    text_align=ft.TextAlign.CENTER, # Ensures multi-line text wraps centered
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=float("inf"), # Forces the alignment container to span the full window width
        ),
        ft.Container(height=20),

    ])


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main(page: ft.Page):
    page.title = "Web Portfolio — Moses Enos P"
    page.padding = 0
    page.scroll = "none"
    page.bgcolor = BG_COLOR

    def route_change(e):
        page.controls.clear()
        route = page.route or "/home"

        route_map = {
            "/home":     ("home",     home_body()),
            "/timeline": ("timeline", timeline_body()),
            "/github":   ("github",   github_body()),
            "/matlab":   ("matlab",   matlab_body()),
            "/blog":     ("blog",     blog_body()),
            "/contact":  ("contact",  contact_body(page)),
        }

        key, body = route_map.get(route, route_map["/home"])
        page.add(page_shell(page, key, body))
        page.update()

    page.on_route_change = route_change
    page.go("/home")


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets",
           port=int(os.getenv("PORT", 8550)))
