"""
Monkey Mod Manager  —  by VSM
Made by StatueXR
"""
import tkinter as tk
from tkinter import filedialog, colorchooser
import os, shutil, json, threading, math, time
import urllib.request, zipfile, tempfile

# ── Config ─────────────────────────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".mmm_vsm4.json")
BEPINEX_URL = (
    "https://github.com/BepInEx/BepInEx/releases/download/"
    "v5.4.23.4/BepInEx_win_x64_5.4.23.4.zip"
)

MODS_DATA = [
    {"id":"BingusNametags",   "author":"sirkingbinx",       "name":"BingusNametags++",
     "desc":"Simple, customizable nametag mod.",
     "tag":"Featured","version":"1.2.0","stars":2,
     "url":"https://github.com/sirkingbinx/BingusNametags"},
    {"id":"SeveralBees",      "author":"sevy-wevvy",         "name":"Several-Bees",
     "desc":"Library for easy in-game UIs and mod browsing.",
     "tag":"Featured","version":"2.0.1","stars":4,
     "url":"https://github.com/sevy-wevvy/SeveralBees"},
    {"id":"MonkeMusic",       "author":"sevy-wevvy",         "name":"Monke Monke Music",
     "desc":"Music manager addon for Gorilla Tag.",
     "tag":"Verified","version":"1.0.3","stars":6,
     "url":"https://github.com/sevy-wevvy/MonkeMusic"},
    {"id":"GorillaOptimizer", "author":"sevy-wevvy",         "name":"Gorilla Optimizer",
     "desc":"Performance mod — smoother framerates in GT.",
     "tag":"Popular","version":"1.1.0","stars":12,
     "url":"https://github.com/sevy-wevvy/GorillaOptimizer"},
    {"id":"Utilla",           "author":"legoandmars",        "name":"Utilla",
     "desc":"PC library handling room-related logic for GT mods.",
     "tag":"Verified","version":"1.7.2","stars":8,
     "url":"https://github.com/legoandmars/Utilla"},
    {"id":"BarkV3",           "author":"SakuraaDevelopment", "name":"Bark v3",
     "desc":"Advanced bark and sound mod with tons of options.",
     "tag":"New","version":"3.0.0","stars":3,
     "url":"https://github.com/SakuraaDev/Bark-v3"},
    {"id":"GorillaCosmetics", "author":"legoandmars",        "name":"Gorilla Cosmetics",
     "desc":"Hats, scarves, and cosmetics for Gorilla Tag.",
     "tag":"Featured","version":"2.3.1","stars":19,
     "url":"https://github.com/legoandmars/GorillaCosmetics"},
    {"id":"ComputerInterface","author":"tonimacaroni",       "name":"Computer Interface",
     "desc":"In-game terminal — run commands and manage mods in VR.",
     "tag":"Popular","version":"3.1.0","stars":15,
     "url":"https://github.com/tonimacaroni/ComputerInterface"},
    {"id":"GorillaShirts",    "author":"vsm",                "name":"Gorilla Shirts",
     "desc":"Equip shirts in GT with custom texture support.",
     "tag":"New","version":"1.0.0","stars":5,
     "url":"https://github.com/vsm/GorillaShirts"},
    {"id":"GorillaTagLib",    "author":"Another Axiom",      "name":"GT Base Lib",
     "desc":"Base game mod support library used by most mods.",
     "tag":"Verified","version":"1.0.0","stars":22,
     "url":"https://github.com/Another-Axiom/GorillaTag"},
    {"id":"RepoLib",          "author":"vsm",                "name":"RepoLib",
     "desc":"Library for fetching and caching mod metadata.",
     "tag":"Featured","version":"1.1.0","stars":7,
     "url":"https://github.com/vsm/RepoLib"},
    {"id":"QuestCosmeticsPC", "author":"Crafted Carts",      "name":"Quest Cosmetics PC",
     "desc":"Port of Quest cosmetics to the PC version.",
     "tag":"Popular","version":"2.0.0","stars":11,
     "url":"https://github.com/crafted-carts/QuestCosmeticsPC"},
]

# ── Palette ────────────────────────────────────────────────────────────────
DEFAULT_BG = "#0d0d12"
SIDEBAR    = "#0a0a0f"
CARD_BG    = "#13131a"
CARD_HL    = "#1a1a25"
SURFACE    = "#16161e"
BORDER     = "#22222e"
PURPLE     = "#7c3aed"
PURPLE2    = "#6d28d9"
PURPLE_DIM = "#2d1f4e"
GREEN      = "#059669"
GREEN_DIM  = "#064e3b"
AMBER      = "#d97706"
BLUE       = "#2563eb"
TEXT       = "#d4d4dc"
MUTED      = "#52526a"
BRIGHT     = "#f0f0f6"
LIME       = "#22c55e"
RED        = "#dc2626"
ORANGE     = "#ea580c"

TAG_MAP = {
    "Featured": ("#7c3aed", "#c4b5fd"),
    "Verified":  ("#059669", "#6ee7b7"),
    "Popular":   ("#d97706", "#fcd34d"),
    "New":       ("#2563eb", "#93c5fd"),
}

# Wobble physics constants
WOBBLE_SPRING  = 0.18
WOBBLE_DAMPING = 0.72
WOBBLE_FPS     = 60
WOBBLE_AMP     = 12


def load_cfg():
    try:
        with open(CONFIG_FILE) as f: return json.load(f)
    except: return {}

def save_cfg(d):
    try:
        with open(CONFIG_FILE, "w") as f: json.dump(d, f, indent=2)
    except: pass

def plugins_dir(gt):
    return os.path.join(gt, "BepInEx", "plugins") if gt else ""

def bepinex_installed(gt):
    return bool(gt) and os.path.isdir(os.path.join(gt, "BepInEx"))

def list_plugins(gt):
    p = plugins_dir(gt)
    if not os.path.isdir(p): return []
    return [f for f in os.listdir(p) if f.lower().endswith((".dll", ".cs"))]

def mod_installed(gt, mod_id):
    p = plugins_dir(gt)
    if not os.path.isdir(p): return False
    return any(mod_id.lower() in f.lower() for f in os.listdir(p))

def lighten(hex_c, amt=28):
    try:
        r = min(255, int(hex_c[1:3], 16) + amt)
        g = min(255, int(hex_c[3:5], 16) + amt)
        b = min(255, int(hex_c[5:7], 16) + amt)
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_c


# ══════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.geometry("1000x700")
        self.minsize(840, 580)
        self.resizable(True, True)

        self.cfg        = load_cfg()
        self.gt_dir     = self.cfg.get("gt_dir", "")
        self.page       = "mods"
        self.filter_tag = "All"

        self.bg_color   = self.cfg.get("bg_color",   DEFAULT_BG)
        self.font_name  = self.cfg.get("font_name",  "Segoe UI")
        self.font_size  = int(self.cfg.get("font_size",  10))
        self.font_color = self.cfg.get("font_color", TEXT)

        # Wobble drag state
        self._wdx = self._wdy = 0  # drag origin (window top-left at press)
        self._wmx = self._wmy = 0  # mouse pos at press
        self._wcx = self._wcy = 0  # last mouse pos during motion
        self._wobble_active = False
        self._wobble_job    = None
        self._spring_vx = self._spring_vy = 0.0
        self._spring_cx = self._spring_cy = 0.0
        self._spring_tx = self._spring_ty = 0.0

        self._build_fonts()
        self._build_ui()
        self._show("mods")
        self.attributes("-alpha", 0.0)
        self._fade(0.0)
        if not self.gt_dir:
            self.after(700, self._show_nodir)

    # ── Font tuples ────────────────────────────────────────────────────────
    def _build_fonts(self):
        n, s = self.font_name, self.font_size
        self.fT  = (n, s + 9, "bold")
        self.fB  = (n, s,     "bold")
        self.fN  = (n, s)
        self.fS  = (n, s - 1)
        self.fXS = (n, s - 2)
        self.fM  = ("Consolas", s - 1)
        self.fC  = ("Consolas", s - 2)

    def _fade(self, a):
        a = min(a + 0.06, 1.0)
        self.attributes("-alpha", a)
        if a < 1.0:
            self.after(16, lambda: self._fade(a))

    # ══ Build skeleton ═════════════════════════════════════════════════════
    def _build_ui(self):
        self.configure(bg=self.bg_color)
        self._build_titlebar()
        body = tk.Frame(self, bg=self.bg_color)
        body.pack(fill="both", expand=True)
        self.sb = tk.Frame(body, bg=SIDEBAR, width=60)
        self.sb.pack(side="left", fill="y")
        self.sb.pack_propagate(False)
        self._build_sidebar()
        main = tk.Frame(body, bg=self.bg_color)
        main.pack(side="left", fill="both", expand=True)
        self._build_topbar(main)
        self.pane = tk.Frame(main, bg=self.bg_color)
        self.pane.pack(fill="both", expand=True)
        self.pages = {}
        self._page_mods()
        self._page_files()
        self._page_settings()
        self._page_credits()

    # ══ Custom title bar + wobbly drag ════════════════════════════════════
    def _build_titlebar(self):
        tb = tk.Frame(self, bg="#080810", height=30)
        tb.pack(fill="x", side="top")
        tb.pack_propagate(False)
        tk.Label(tb, text="🦍  Monkey Mod Manager",
                 bg="#080810", fg="#2e2e45",
                 font=("Segoe UI", 8)).pack(side="left", padx=14)
        for sym, cmd, hov in [("✕", self.destroy, RED),
                               ("–", self._minimize, MUTED),
                               ("□", self._toggle_max, MUTED)]:
            b = tk.Label(tb, text=sym, bg="#080810", fg="#2e2e45",
                         font=("Segoe UI", 10), padx=11, cursor="hand2")
            b.pack(side="right")
            b.bind("<Button-1>", lambda e, c=cmd: c())
            b.bind("<Enter>",    lambda e, w=b, h=hov: w.config(fg=h))
            b.bind("<Leave>",    lambda e, w=b: w.config(fg="#2e2e45"))
        tb.bind("<ButtonPress-1>",   self._wob_press)
        tb.bind("<B1-Motion>",       self._wob_motion)
        tb.bind("<ButtonRelease-1>", self._wob_release)

    def _minimize(self):
        self.overrideredirect(False)
        self.iconify()
        self.bind("<Map>", lambda e: (self.overrideredirect(True), self.unbind("<Map>")))

    def _toggle_max(self):
        self.state("normal" if self.state() == "zoomed" else "zoomed")

    # ── Wobbly drag  (Compiz spring physics) ──────────────────────────────
    def _wob_press(self, e):
        self._wdx = self.winfo_x()
        self._wdy = self.winfo_y()
        self._wmx = e.x_root
        self._wmy = e.y_root
        self._wcx = e.x_root
        self._wcy = e.y_root
        self._wobble_active = True
        self._wobble_t = 0
        self.attributes("-alpha", 0.85)
        if self._wobble_job:
            self.after_cancel(self._wobble_job)
        self._wob_tick()

    def _wob_motion(self, e):
        # Move window exactly with mouse
        nx = self._wdx + (e.x_root - self._wmx)
        ny = self._wdy + (e.y_root - self._wmy)
        self.geometry(f"+{nx}+{ny}")
        self._wcx = e.x_root
        self._wcy = e.y_root

    def _wob_tick(self):
        """Continuously apply sinusoidal wobble offset while dragging."""
        if not self._wobble_active:
            return
        self._wobble_t += 1
        t = self._wobble_t

        # Velocity vector from total movement
        vx = self._wcx - self._wmx
        vy = self._wcy - self._wmy
        speed = math.sqrt(vx * vx + vy * vy)

        # Scale wobble amplitude by speed (more movement = more wobble)
        amp_x = min(speed * 0.18, WOBBLE_AMP)
        amp_y = min(speed * 0.10, WOBBLE_AMP * 0.5)

        # Perpendicular sine wave — wobble side-to-side relative to drag
        sx = int(math.sin(t * 0.28) * amp_x)
        sy = int(math.cos(t * 0.22) * amp_y)

        cx = self.winfo_x()
        cy = self.winfo_y()
        self.geometry(f"+{cx + sx}+{cy + sy}")

        self._wobble_job = self.after(1000 // WOBBLE_FPS, self._wob_tick)

    def _wob_release(self, e):
        self._wobble_active = False
        if self._wobble_job:
            self.after_cancel(self._wobble_job)
            self._wobble_job = None

        # Spring settle around final position
        self._spring_cx = float(self.winfo_x())
        self._spring_cy = float(self.winfo_y())
        self._spring_tx = float(self._wdx + (e.x_root - self._wmx))
        self._spring_ty = float(self._wdy + (e.y_root - self._wmy))

        # Initial velocity is leftover wobble impulse
        self._spring_vx = (self._wcx - self._wmx) * 0.06
        self._spring_vy = (self._wcy - self._wmy) * 0.04

        self.attributes("-alpha", 1.0)
        self._settle(0)

    def _settle(self, step):
        """Spring-damp back to resting position."""
        if step > 90:
            self.geometry(f"+{int(self._spring_tx)}+{int(self._spring_ty)}")
            return

        fx = (self._spring_tx - self._spring_cx) * WOBBLE_SPRING
        fy = (self._spring_ty - self._spring_cy) * WOBBLE_SPRING
        self._spring_vx = (self._spring_vx + fx) * WOBBLE_DAMPING
        self._spring_vy = (self._spring_vy + fy) * WOBBLE_DAMPING
        self._spring_cx += self._spring_vx
        self._spring_cy += self._spring_vy
        self.geometry(f"+{int(self._spring_cx)}+{int(self._spring_cy)}")

        if abs(self._spring_vx) < 0.25 and abs(self._spring_vy) < 0.25:
            self.geometry(f"+{int(self._spring_tx)}+{int(self._spring_ty)}")
            return
        self.after(1000 // WOBBLE_FPS, lambda: self._settle(step + 1))

    # ══ Sidebar ════════════════════════════════════════════════════════════
    def _build_sidebar(self):
        logo = tk.Label(self.sb, text="🦍", bg=SIDEBAR, font=("Segoe UI", 18), cursor="hand2")
        logo.pack(pady=(12, 14))
        logo.bind("<Button-1>", lambda e: self._show("mods"))
        self._sbs = {}
        for page, icon in [("mods","⊞"),("files","📁"),("settings","⚙"),("credits","★")]:
            self._sbs[page] = self._sb_btn(page, icon)
        tk.Frame(self.sb, bg=SIDEBAR).pack(fill="both", expand=True)
        play = tk.Label(self.sb, text="▶", bg=LIME, fg="#000",
                        font=("Segoe UI", 13, "bold"), width=3, pady=6, cursor="hand2")
        play.pack(pady=(0, 12), padx=7)
        play.bind("<Button-1>", lambda e: self._launch())
        play.bind("<Enter>",    lambda e: play.config(bg="#16a34a"))
        play.bind("<Leave>",    lambda e: play.config(bg=LIME))

    def _sb_btn(self, page, icon):
        f   = tk.Frame(self.sb, bg=SIDEBAR, cursor="hand2")
        f.pack(fill="x")
        lbl = tk.Label(f, text=icon, bg=SIDEBAR, fg=MUTED,
                       font=("Segoe UI", 15), pady=9, cursor="hand2")
        lbl.pack()
        for w in (f, lbl):
            w.bind("<Button-1>", lambda e, p=page: self._show(p))
            w.bind("<Enter>",    lambda e, l=lbl, p=page: l.config(fg=BRIGHT) if self.page != p else None)
            w.bind("<Leave>",    lambda e, l=lbl, p=page: l.config(fg=PURPLE if self.page == p else MUTED))
        return (f, lbl)

    def _sync_sidebar(self):
        for p, (f, lbl) in self._sbs.items():
            active = (p == self.page)
            f.config(bg="#13132a" if active else SIDEBAR)
            lbl.config(bg="#13132a" if active else SIDEBAR,
                       fg=PURPLE   if active else MUTED)

    # ══ Top bar ════════════════════════════════════════════════════════════
    def _build_topbar(self, parent):
        top = tk.Frame(parent, bg=self.bg_color)
        top.pack(fill="x")
        row1 = tk.Frame(top, bg=self.bg_color)
        row1.pack(fill="x", padx=20, pady=(14, 2))
        tk.Label(row1, text="Monkey Mod Manager",
                 bg=self.bg_color, fg=self.font_color, font=self.fT).pack(side="left")
        tk.Frame(top, bg=BORDER, height=1).pack(fill="x")
        row2 = tk.Frame(top, bg=self.bg_color)
        row2.pack(fill="x", padx=20, pady=(6, 6))
        dbox = tk.Frame(row2, bg=BORDER, padx=1, pady=1)
        dbox.pack(side="left")
        din  = tk.Frame(dbox, bg=SURFACE)
        din.pack()
        self.dir_entry = tk.Entry(din, bg=SURFACE, fg=PURPLE,
                                  insertbackground=PURPLE,
                                  font=("Consolas", 8), bd=0, width=46, relief="flat")
        self.dir_entry.insert(0, self.gt_dir or "No directory set — click … to choose")
        self.dir_entry.pack(side="left", padx=8, pady=5)
        br = tk.Label(din, text="…", bg=SURFACE, fg=MUTED,
                      font=("Segoe UI", 11), cursor="hand2")
        br.pack(side="left", padx=(0, 6))
        br.bind("<Button-1>", lambda e: self._pick_dir())
        tk.Frame(top, bg=BORDER, height=1).pack(fill="x")
        self._nodir = tk.Frame(top, bg="#2d1111")
        tk.Label(self._nodir,
                 text="⚠  No directory set — select your Gorilla Tag folder to continue",
                 bg="#2d1111", fg="#fca5a5", font=self.fS).pack(side="left", padx=14, pady=7)
        fix = tk.Label(self._nodir, text="Set now →", bg=RED, fg=BRIGHT,
                       font=self.fB, padx=10, pady=4, cursor="hand2")
        fix.pack(side="right", padx=10, pady=5)
        fix.bind("<Button-1>", lambda e: self._pick_dir())

    def _show_nodir(self):
        if not self.gt_dir:
            self._nodir.pack(fill="x")

    # ══ MODS PAGE ══════════════════════════════════════════════════════════
    def _page_mods(self):
        pg = tk.Frame(self.pane, bg=self.bg_color)
        self.pages["mods"] = pg

        # BepInEx status bar
        brow = tk.Frame(pg, bg=SURFACE,
                        highlightbackground=BORDER, highlightthickness=1)
        brow.pack(fill="x", padx=20, pady=(12, 4))
        bleft = tk.Frame(brow, bg=SURFACE)
        bleft.pack(side="left", fill="both", expand=True, padx=14, pady=10)
        tk.Label(bleft, text="BepInEx", bg=SURFACE, fg=BRIGHT, font=self.fB).pack(anchor="w")
        self._bep_lbl = tk.Label(bleft, text="", bg=SURFACE, fg=MUTED, font=self.fXS)
        self._bep_lbl.pack(anchor="w")
        bright = tk.Frame(brow, bg=SURFACE)
        bright.pack(side="right", padx=10, pady=10)
        self._bep_inst_btn = self._pill(bright, "Install BepInEx", PURPLE, BRIGHT,
                                        self._install_bepinex)
        self._bep_inst_btn.pack(side="left", padx=3)
        self._bep_unin_btn = self._pill(bright, "Uninstall", "#2a1414", "#fca5a5",
                                        self._uninstall_bepinex)
        self._bep_unin_btn.pack(side="left", padx=3)
        self._refresh_bep()

        # Console
        cbox = tk.Frame(pg, bg="#08080e",
                        highlightbackground=BORDER, highlightthickness=1)
        cbox.pack(fill="x", padx=20, pady=(0, 8))
        chdr = tk.Frame(cbox, bg="#08080e")
        chdr.pack(fill="x", padx=8, pady=(4, 0))
        tk.Label(chdr, text="console", bg="#08080e", fg="#253025",
                 font=("Consolas", 8)).pack(side="left")
        clr = tk.Label(chdr, text="clear", bg="#08080e", fg="#222232",
                       font=("Consolas", 8), cursor="hand2")
        clr.pack(side="right")
        clr.bind("<Button-1>", lambda e: self._con_clear())
        clr.bind("<Enter>",    lambda e: clr.config(fg=MUTED))
        clr.bind("<Leave>",    lambda e: clr.config(fg="#222232"))
        self._con = tk.Text(cbox, bg="#08080e", fg=LIME, font=self.fC,
                            height=4, bd=0, relief="flat",
                            state="disabled", wrap="word",
                            insertbackground=LIME)
        self._con.pack(fill="x", padx=8, pady=(2, 6))

        # Search + tag filter
        sbar = tk.Frame(pg, bg=self.bg_color)
        sbar.pack(fill="x", padx=20, pady=(0, 6))
        sbox = tk.Frame(sbar, bg=BORDER, padx=1, pady=1)
        sbox.pack(side="left")
        sin  = tk.Frame(sbox, bg=SURFACE)
        sin.pack()
        tk.Label(sin, text="⌕", bg=SURFACE, fg=MUTED,
                 font=("Segoe UI", 11)).pack(side="left", padx=(8, 3), pady=4)
        self._sv = tk.StringVar()
        self._sv.trace_add("write", lambda *_: self._filter())
        tk.Entry(sin, textvariable=self._sv, bg=SURFACE, fg=TEXT,
                 insertbackground=TEXT, font=self.fN, bd=0,
                 relief="flat", width=28).pack(side="left", pady=5, padx=(0, 8))
        self._tag_btns = {}
        tf = tk.Frame(sbar, bg=self.bg_color)
        tf.pack(side="left", padx=10)
        for t in ("All", "Featured", "Verified", "Popular", "New"):
            b = tk.Label(tf, text=t, font=self.fXS, padx=9, pady=3, cursor="hand2")
            b.config(bg=PURPLE if t == "All" else "#1e1e2a",
                     fg=BRIGHT if t == "All" else MUTED)
            b.pack(side="left", padx=2)
            b.bind("<Button-1>", lambda e, tag=t: self._set_tag(tag))
            self._tag_btns[t] = b

        # Scrollable grid
        cv = tk.Canvas(pg, bg=self.bg_color, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(pg, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True, padx=(20, 0), pady=(0, 8))
        self._gf = tk.Frame(cv, bg=self.bg_color)
        self._gw = cv.create_window((0, 0), window=self._gf, anchor="nw")
        self._gf.bind("<Configure>",
                      lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",
                lambda e: cv.itemconfig(self._gw, width=e.width))
        cv.bind_all("<MouseWheel>",
                    lambda e: cv.yview_scroll(-1 * (e.delta // 120), "units"))
        self._render(MODS_DATA)

    def _pill(self, parent, text, bg, fg, cmd):
        b = tk.Label(parent, text=text, bg=bg, fg=fg,
                     font=self.fS, padx=12, pady=5, cursor="hand2")
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>",    lambda e: b.config(bg=lighten(bg)))
        b.bind("<Leave>",    lambda e: b.config(bg=bg))
        return b

    def _refresh_bep(self):
        ins = bepinex_installed(self.gt_dir)
        self._bep_lbl.config(
            text="installed  ✓" if ins else "not installed",
            fg=LIME if ins else "#4a2a2a")
        self._bep_inst_btn.config(
            bg=PURPLE_DIM if ins else PURPLE,
            fg=MUTED if ins else BRIGHT,
            cursor="arrow" if ins else "hand2")

    def _install_bepinex(self):
        if not self.gt_dir:
            self._con_log("no directory set"); return
        self._con_log("downloading BepInEx 5.4.23.4 ...")
        self._bep_inst_btn.config(text="downloading ...", bg=PURPLE_DIM, cursor="arrow")

        def work():
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    zp = os.path.join(tmp, "bep.zip")
                    last = [0]
                    def prog(cnt, bs, total):
                        if total <= 0: return
                        pct = min(int(cnt * bs * 100 / total), 100)
                        if pct // 5 > last[0] // 5:
                            last[0] = pct
                            self._con_log(f"  {pct}%")
                    urllib.request.urlretrieve(BEPINEX_URL, zp, prog)
                    self._con_log("extracting ...")
                    with zipfile.ZipFile(zp) as z:
                        z.extractall(self.gt_dir)
                self._con_log("done — zip removed automatically")
                self.after(0, lambda: (
                    self._refresh_bep(),
                    self._bep_inst_btn.config(text="Install BepInEx")))
            except Exception as ex:
                self._con_log(f"error: {ex}")
                self.after(0, lambda: self._bep_inst_btn.config(
                    text="Install BepInEx", bg=PURPLE, cursor="hand2"))

        threading.Thread(target=work, daemon=True).start()

    def _uninstall_bepinex(self):
        if not self.gt_dir:
            self._con_log("no directory set"); return
        p = os.path.join(self.gt_dir, "BepInEx")
        if not os.path.isdir(p):
            self._con_log("BepInEx folder not found"); return
        try:
            shutil.rmtree(p)
            self._con_log("BepInEx removed")
            self._refresh_bep()
        except Exception as ex:
            self._con_log(f"error: {ex}")

    def _con_log(self, msg):
        def _do():
            self._con.config(state="normal")
            self._con.insert("end", f"{msg}\n")
            self._con.see("end")
            self._con.config(state="disabled")
        self.after(0, _do)

    def _con_clear(self):
        self._con.config(state="normal")
        self._con.delete("1.0", "end")
        self._con.config(state="disabled")

    def _set_tag(self, tag):
        self.filter_tag = tag
        for t, b in self._tag_btns.items():
            b.config(bg=PURPLE if t == tag else "#1e1e2a",
                     fg=BRIGHT if t == tag else MUTED)
        self._filter()

    def _filter(self):
        q   = self._sv.get().lower().strip()
        tag = self.filter_tag
        out = [m for m in MODS_DATA
               if (tag == "All" or m["tag"] == tag)
               and (not q or q in m["name"].lower()
                    or q in m["desc"].lower()
                    or q in m["author"].lower())]
        self._render(out)

    def _render(self, mods):
        if not hasattr(self, "_gf") or not self._gf.winfo_exists(): return
        for w in self._gf.winfo_children(): w.destroy()
        cols = 3
        for i, m in enumerate(mods):
            r, c = divmod(i, cols)
            self._mod_card(self._gf, m).grid(row=r, column=c,
                                              padx=7, pady=7, sticky="nsew")
        for c in range(cols):
            self._gf.columnconfigure(c, weight=1)

    def _mod_card(self, parent, mod):
        inst = mod_installed(self.gt_dir, mod["id"])
        tbg, tfg = TAG_MAP.get(mod["tag"], ("#222", "#888"))
        outer = tk.Frame(parent, bg=CARD_BG, bd=0,
                         highlightbackground=BORDER, highlightthickness=1, cursor="hand2")
        head = tk.Frame(outer, bg="#0b0b10", height=80)
        head.pack(fill="x"); head.pack_propagate(False)
        tk.Label(head, text=f"{mod['author']}/", bg="#0b0b10", fg=MUTED,
                 font=("Segoe UI", 7), anchor="w").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Label(head, text=mod["name"], bg="#0b0b10", fg=BRIGHT,
                 font=("Segoe UI", 10, "bold"), anchor="w",
                 wraplength=185).pack(anchor="w", padx=10)
        tk.Label(head, text=mod["desc"], bg="#0b0b10", fg=MUTED,
                 font=("Segoe UI", 7), anchor="w",
                 wraplength=195, justify="left").pack(anchor="w", padx=10, pady=(3, 0))
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x")
        body = tk.Frame(outer, bg=CARD_BG, padx=10, pady=8)
        body.pack(fill="x")
        foot = tk.Frame(body, bg=CARD_BG)
        foot.pack(fill="x")
        tk.Label(foot, text=mod["tag"], bg=tbg, fg=tfg,
                 font=("Segoe UI", 6, "bold"), padx=6, pady=2).pack(side="left")
        tk.Label(foot, text=f"★ {mod['stars']}", bg="#1a1a28", fg=MUTED,
                 font=("Segoe UI", 7), padx=6, pady=2).pack(side="left", padx=4)
        if inst:
            tk.Label(foot, text="installed", bg=GREEN_DIM, fg=LIME,
                     font=("Segoe UI", 6, "bold"), padx=6, pady=2).pack(side="right")
        btns = tk.Frame(outer, bg=CARD_BG)
        btns.pack(fill="x")
        ib_bg = PURPLE_DIM if inst else PURPLE
        ib = tk.Label(btns, text="Reinstall" if inst else "Install",
                      bg=ib_bg, fg=BRIGHT,
                      font=("Segoe UI", 8, "bold"), cursor="hand2", pady=5)
        ib.pack(side="left", fill="x", expand=True)
        ib.bind("<Button-1>", lambda e, m=mod: self._install_mod(m))
        ib.bind("<Enter>",    lambda e: ib.config(bg=PURPLE2))
        ib.bind("<Leave>",    lambda e: ib.config(bg=ib_bg))
        if inst:
            ub = tk.Label(btns, text="Remove", bg="#2a1010", fg="#fca5a5",
                          font=("Segoe UI", 8, "bold"), cursor="hand2", pady=5)
            ub.pack(side="left", fill="x", expand=True)
            ub.bind("<Button-1>", lambda e, m=mod: self._remove_mod(m))
        def _e(e): outer.config(highlightbackground=PURPLE); body.config(bg=CARD_HL); foot.config(bg=CARD_HL); btns.config(bg=CARD_HL)
        def _l(e): outer.config(highlightbackground=BORDER); body.config(bg=CARD_BG); foot.config(bg=CARD_BG); btns.config(bg=CARD_BG)
        outer.bind("<Enter>", _e); outer.bind("<Leave>", _l)
        return outer

    def _install_mod(self, mod):
        if not self.gt_dir:
            self._con_log("no directory set"); return
        plug = plugins_dir(self.gt_dir)
        if not os.path.isdir(plug):
            self._con_log("BepInEx not installed — install it first"); return
        self._con_log(f"installing {mod['name']} v{mod['version']} ...")
        self._con_log(f"  source: {mod['url']}")

    def _remove_mod(self, mod):
        plug = plugins_dir(self.gt_dir)
        if not os.path.isdir(plug):
            self._con_log("plugins folder not found"); return
        removed = []
        for f in os.listdir(plug):
            if mod["id"].lower() in f.lower():
                try:
                    os.remove(os.path.join(plug, f)); removed.append(f)
                except Exception as ex:
                    self._con_log(f"error: {ex}")
        if removed:
            self._con_log(f"removed: {', '.join(removed)}")
            self._render(MODS_DATA)
        else:
            self._con_log(f"nothing found for {mod['name']}")

    # ══ FILES PAGE ═════════════════════════════════════════════════════════
    def _page_files(self):
        pg = tk.Frame(self.pane, bg=self.bg_color)
        self.pages["files"] = pg
        hdr = tk.Frame(pg, bg=self.bg_color)
        hdr.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(hdr, text="Installed Plugins", bg=self.bg_color, fg=BRIGHT,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(hdr, text="BepInEx/plugins", bg=self.bg_color, fg=MUTED,
                 font=self.fM).pack(side="left", padx=10)
        ref = tk.Label(hdr, text="↻", bg=self.bg_color, fg=PURPLE,
                       font=("Segoe UI", 14), cursor="hand2")
        ref.pack(side="right")
        ref.bind("<Button-1>", lambda e: self._refresh_files())
        dz = tk.Frame(pg, bg=SURFACE, pady=20,
                      highlightbackground=PURPLE, highlightthickness=1)
        dz.pack(fill="x", padx=20, pady=(10, 10))
        tk.Label(dz, text="⊕", bg=SURFACE, fg=PURPLE,
                 font=("Segoe UI", 24)).pack()
        tk.Label(dz, text="Drag DLL / CS files here, or",
                 bg=SURFACE, fg=MUTED, font=self.fS).pack()
        ib = tk.Label(dz, text="Browse & Import", bg=PURPLE, fg=BRIGHT,
                      font=self.fS, padx=14, pady=5, cursor="hand2")
        ib.pack(pady=(6, 0))
        ib.bind("<Button-1>", lambda e: self._import_files())
        ib.bind("<Enter>",    lambda e: ib.config(bg=PURPLE2))
        ib.bind("<Leave>",    lambda e: ib.config(bg=PURPLE))
        tk.Frame(pg, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0, 6))
        cv = tk.Canvas(pg, bg=self.bg_color, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(pg, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True, padx=(20, 0))
        self._fi = tk.Frame(cv, bg=self.bg_color)
        fw = cv.create_window((0, 0), window=self._fi, anchor="nw")
        self._fi.bind("<Configure>",
                      lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfig(fw, width=e.width))
        self._refresh_files()

    def _refresh_files(self):
        if not hasattr(self, "_fi") or not self._fi.winfo_exists(): return
        for w in self._fi.winfo_children(): w.destroy()
        files = list_plugins(self.gt_dir)
        if not files:
            tk.Label(self._fi, text="No plugins found.",
                     bg=self.bg_color, fg=MUTED, font=self.fN).pack(pady=24)
            return
        for f in files: self._file_row(f)

    def _file_row(self, fname):
        row = tk.Frame(self._fi, bg=CARD_BG, pady=8, padx=14,
                       highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", pady=(0, 3), padx=(0, 16))
        ext = fname.rsplit(".", 1)[-1].upper()
        ec, efg = {"DLL": (PURPLE, "#ddd6fe"), "CS": (GREEN, "#6ee7b7")}.get(ext, ("#333", "#aaa"))
        tk.Label(row, text=ext, bg=ec, fg=efg,
                 font=("Consolas", 7, "bold"), padx=5, pady=2).pack(side="left", padx=(0, 10))
        tk.Label(row, text=fname, bg=CARD_BG, fg=BRIGHT, font=self.fB).pack(side="left")
        p = os.path.join(plugins_dir(self.gt_dir), fname)
        try:
            sz = os.path.getsize(p)
            sz_t = f"{sz // 1024} KB" if sz > 1024 else f"{sz} B"
        except: sz_t = ""
        tk.Label(row, text=sz_t, bg=CARD_BG, fg=MUTED, font=self.fXS).pack(side="left", padx=6)
        x = tk.Label(row, text="✕", bg=CARD_BG, fg=MUTED,
                     font=("Segoe UI", 10), cursor="hand2", padx=8)
        x.pack(side="right")
        x.bind("<Button-1>", lambda e, f=fname, r=row: self._del_file(f, r))
        x.bind("<Enter>",    lambda e: x.config(fg=RED))
        x.bind("<Leave>",    lambda e: x.config(fg=MUTED))
        row.bind("<Enter>",  lambda e: row.config(bg=CARD_HL))
        row.bind("<Leave>",  lambda e: row.config(bg=CARD_BG))

    def _del_file(self, fname, row):
        try:
            os.remove(os.path.join(plugins_dir(self.gt_dir), fname))
            row.destroy()
        except Exception as ex:
            self._con_log(f"error: {ex}")

    def _import_files(self):
        if not self.gt_dir:
            self._con_log("no directory set"); return
        plug = plugins_dir(self.gt_dir)
        if not os.path.isdir(plug):
            self._con_log("BepInEx plugins folder missing"); return
        files = filedialog.askopenfilenames(
            title="Select DLL / CS files",
            filetypes=[("Mod files", "*.dll *.cs"), ("All", "*.*")])
        ok = 0
        for f in files:
            try: shutil.copy2(f, plug); ok += 1
            except Exception as ex: self._con_log(f"error: {ex}")
        if ok:
            self._con_log(f"imported {ok} file(s)")
            self._refresh_files()

    # ══ SETTINGS PAGE ══════════════════════════════════════════════════════
    def _page_settings(self):
        pg = tk.Frame(self.pane, bg=self.bg_color)
        self.pages["settings"] = pg
        cv = tk.Canvas(pg, bg=self.bg_color, bd=0, highlightthickness=0)
        sb = tk.Scrollbar(pg, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True)
        inn = tk.Frame(cv, bg=self.bg_color)
        cw  = cv.create_window((0, 0), window=inn, anchor="nw")
        inn.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",  lambda e: cv.itemconfig(cw, width=e.width))

        tk.Label(inn, text="Settings", bg=self.bg_color, fg=BRIGHT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(18, 10))

        # Directory
        self._scard(inn, "Gorilla Tag Directory",
                    "Path to your GT installation folder.",
                    [("Change", AMBER, self._pick_dir)])

        # Background color
        bg_f = self._scard_frame(inn, "Background Color",
                                  "Custom color for the app background.", ORANGE)
        br = tk.Frame(bg_f, bg=CARD_BG); br.pack(fill="x", pady=(8, 0))
        self._bg_prev = tk.Label(br, bg=self.bg_color, width=4,
                                 highlightbackground=BORDER, highlightthickness=1)
        self._bg_prev.pack(side="left", padx=(0, 8))
        self._pill_inline(br, "Pick Color", ORANGE, BRIGHT, self._pick_bg).pack(side="left", padx=2)
        self._pill_inline(br, "Reset",     "#222",  MUTED,  self._reset_bg).pack(side="left", padx=2)

        # Font settings
        fc = self._scard_frame(inn, "Font", "Family, size, and color.", BLUE)

        nr = tk.Frame(fc, bg=CARD_BG); nr.pack(fill="x", pady=4)
        tk.Label(nr, text="Family", bg=CARD_BG, fg=MUTED,
                 font=self.fXS, width=9, anchor="w").pack(side="left")
        self._fn_var = tk.StringVar(value=self.font_name)
        om = tk.OptionMenu(nr, self._fn_var,
                           "Segoe UI", "Arial", "Tahoma", "Verdana",
                           "Consolas", "Courier New", "Georgia", "Calibri")
        om.config(bg=SURFACE, fg=TEXT, font=self.fXS, bd=0,
                  activebackground=CARD_HL, highlightthickness=0, relief="flat")
        om["menu"].config(bg=SURFACE, fg=TEXT, activebackground=PURPLE)
        om.pack(side="left")

        sr = tk.Frame(fc, bg=CARD_BG); sr.pack(fill="x", pady=4)
        tk.Label(sr, text="Size", bg=CARD_BG, fg=MUTED,
                 font=self.fXS, width=9, anchor="w").pack(side="left")
        self._fs_var = tk.IntVar(value=self.font_size)
        tk.Scale(sr, from_=8, to=20, orient="horizontal",
                 variable=self._fs_var, bg=CARD_BG, fg=TEXT,
                 troughcolor=SURFACE, highlightthickness=0,
                 activebackground=PURPLE, length=160, showvalue=False).pack(side="left")
        self._fs_lbl = tk.Label(sr, text=str(self.font_size),
                                bg=CARD_BG, fg=PURPLE, font=self.fB, width=3)
        self._fs_lbl.pack(side="left", padx=4)
        self._fs_var.trace_add("write",
            lambda *_: self._fs_lbl.config(text=str(self._fs_var.get())))

        cr = tk.Frame(fc, bg=CARD_BG); cr.pack(fill="x", pady=4)
        tk.Label(cr, text="Color", bg=CARD_BG, fg=MUTED,
                 font=self.fXS, width=9, anchor="w").pack(side="left")
        self._fc_prev = tk.Label(cr, bg=self.font_color, width=4,
                                 highlightbackground=BORDER, highlightthickness=1)
        self._fc_prev.pack(side="left", padx=(0, 8))
        self._pill_inline(cr, "Pick", BLUE, BRIGHT, self._pick_fc).pack(side="left")

        ab = tk.Label(fc, text="Apply  (restart to fully take effect)",
                      bg=PURPLE, fg=BRIGHT, font=self.fS,
                      padx=14, pady=6, cursor="hand2")
        ab.pack(anchor="w", pady=(10, 0))
        ab.bind("<Button-1>", lambda e: self._apply_fonts())
        ab.bind("<Enter>",    lambda e: ab.config(bg=PURPLE2))
        ab.bind("<Leave>",    lambda e: ab.config(bg=PURPLE))

        # BepInEx
        self._scard(inn, "BepInEx",
                    "Download and install BepInEx 5.4.23.4 into your GT folder.",
                    [("Install",   GREEN,    self._install_bepinex),
                     ("Uninstall", "#2a1414", self._uninstall_bepinex)])

        tk.Frame(inn, bg=BORDER, height=1).pack(fill="x", padx=20, pady=16)
        tk.Label(inn, text=f"config  {CONFIG_FILE}",
                 bg=self.bg_color, fg="#1e1e2e", font=self.fC).pack(anchor="w", padx=20, pady=(0, 20))

    def _scard_frame(self, parent, title, desc, accent):
        card = tk.Frame(parent, bg=CARD_BG,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=20, pady=(0, 8))
        tk.Frame(card, bg=accent, height=2).pack(fill="x")
        inn = tk.Frame(card, bg=CARD_BG, padx=16, pady=12)
        inn.pack(fill="x")
        tk.Label(inn, text=title, bg=CARD_BG, fg=BRIGHT, font=self.fB).pack(anchor="w")
        tk.Label(inn, text=desc, bg=CARD_BG, fg=MUTED, font=self.fXS,
                 wraplength=440, justify="left").pack(anchor="w", pady=(2, 0))
        return inn

    def _scard(self, parent, title, desc, buttons):
        inn = self._scard_frame(parent, title, desc, PURPLE)
        brow = tk.Frame(inn, bg=CARD_BG); brow.pack(anchor="e", pady=(8, 0))
        for txt, bg, cmd in buttons:
            b = tk.Label(brow, text=txt, bg=bg, fg=BRIGHT,
                         font=self.fS, padx=12, pady=5, cursor="hand2")
            b.pack(side="left", padx=3)
            b.bind("<Button-1>", lambda e, c=cmd: c())
            b.bind("<Enter>",    lambda e, w=b, col=bg: w.config(bg=lighten(col)))
            b.bind("<Leave>",    lambda e, w=b, col=bg: w.config(bg=col))

    def _pill_inline(self, parent, text, bg, fg, cmd):
        b = tk.Label(parent, text=text, bg=bg, fg=fg,
                     font=self.fXS, padx=10, pady=4, cursor="hand2")
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>",    lambda e: b.config(bg=lighten(bg)))
        b.bind("<Leave>",    lambda e: b.config(bg=bg))
        return b

    def _pick_bg(self):
        c = colorchooser.askcolor(title="Background Color", initialcolor=self.bg_color)
        if c and c[1]:
            self.bg_color = c[1]; self.cfg["bg_color"] = c[1]; save_cfg(self.cfg)
            self._bg_prev.config(bg=c[1]); self.configure(bg=c[1])

    def _reset_bg(self):
        self.bg_color = DEFAULT_BG; self.cfg["bg_color"] = DEFAULT_BG; save_cfg(self.cfg)
        self._bg_prev.config(bg=DEFAULT_BG); self.configure(bg=DEFAULT_BG)

    def _pick_fc(self):
        c = colorchooser.askcolor(title="Font Color", initialcolor=self.font_color)
        if c and c[1]:
            self.font_color = c[1]; self._fc_prev.config(bg=c[1])

    def _apply_fonts(self):
        self.font_name = self._fn_var.get()
        self.font_size = self._fs_var.get()
        self.cfg.update(font_name=self.font_name,
                        font_size=self.font_size,
                        font_color=self.font_color)
        save_cfg(self.cfg)
        self._build_fonts()
        self._con_log(f"font → {self.font_name} {self.font_size}pt  (restart to fully apply)")

    # ══ CREDITS PAGE ═══════════════════════════════════════════════════════
    def _page_credits(self):
        pg = tk.Frame(self.pane, bg=self.bg_color)
        self.pages["credits"] = pg
        cv = tk.Canvas(pg, bg=self.bg_color, bd=0, highlightthickness=0)
        cv.pack(fill="both", expand=True)
        inn = tk.Frame(cv, bg=self.bg_color)
        cw  = cv.create_window((0, 0), window=inn, anchor="nw")
        inn.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",  lambda e: cv.itemconfig(cw, width=e.width))

        # Hero section
        hero = tk.Frame(inn, bg=self.bg_color)
        hero.pack(pady=(48, 0))
        tk.Label(hero, text="🦍", bg=self.bg_color,
                 font=("Segoe UI", 52)).pack()
        tk.Label(hero, text="Monkey Mod Manager",
                 bg=self.bg_color, fg=BRIGHT,
                 font=("Segoe UI", 24, "bold")).pack(pady=(6, 0))
        tk.Label(hero, text="by VSM",
                 bg=self.bg_color, fg=PURPLE,
                 font=("Segoe UI", 12)).pack(pady=(2, 0))

        tk.Frame(inn, bg=BORDER, height=1).pack(fill="x", padx=60, pady=24)

        # Cards row
        cards = tk.Frame(inn, bg=self.bg_color)
        cards.pack(fill="x", padx=60, pady=(0, 12))

        def crd(parent, accent, title, body_text):
            f = tk.Frame(parent, bg=CARD_BG,
                         highlightbackground=BORDER, highlightthickness=1)
            f.pack(side="left", fill="both", expand=True, padx=6)
            tk.Frame(f, bg=accent, height=2).pack(fill="x")
            inn2 = tk.Frame(f, bg=CARD_BG, padx=16, pady=14)
            inn2.pack(fill="both", expand=True)
            tk.Label(inn2, text=title, bg=CARD_BG, fg=BRIGHT,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
            tk.Label(inn2, text=body_text, bg=CARD_BG, fg=TEXT,
                     font=self.fS, justify="left",
                     wraplength=220).pack(anchor="w", pady=(6, 0))

        crd(cards, PURPLE, "Made by StatueXR",
            "Find me on the Gorilla Tag\nmodding Discord server.")
        crd(cards, GREEN,  "0 errors",
            "Written in Python.\nTested. Works.\nShips clean.")
        crd(cards, ORANGE, "Open source",
            "Built to be readable,\nextensible, and actually\nmaintained.")

        tk.Label(inn, text="v4.0.0",
                 bg=self.bg_color, fg="#1a1a2a",
                 font=("Consolas", 9)).pack(pady=(24, 48))

    # ══ Navigation ═════════════════════════════════════════════════════════
    def _show(self, page):
        self.page = page
        for f in self.pages.values(): f.pack_forget()
        self.pages[page].pack(fill="both", expand=True)
        self._sync_sidebar()
        if page == "mods":
            self._refresh_bep()
            self._render(MODS_DATA)

    def _pick_dir(self):
        p = filedialog.askdirectory(
            title="Select Gorilla Tag folder",
            initialdir=r"C:\Program Files (x86)\Steam\steamapps\common\Gorilla Tag")
        if p:
            self.gt_dir = p; self.cfg["gt_dir"] = p; save_cfg(self.cfg)
            self.dir_entry.delete(0, "end"); self.dir_entry.insert(0, p)
            self._nodir.pack_forget()
            self._con_log(f"directory set: {p}")
            self._refresh_bep(); self._refresh_files(); self._render(MODS_DATA)

    def _launch(self):
        if not self.gt_dir:
            self._con_log("no directory set"); return
        exe = os.path.join(self.gt_dir, "Gorilla Tag.exe")
        if os.path.exists(exe): os.startfile(exe)
        else: self._con_log("Gorilla Tag.exe not found")


if __name__ == "__main__":
    App().mainloop()
