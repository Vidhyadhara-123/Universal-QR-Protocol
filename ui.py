import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import ImageTk, Image, ImageDraw
import io
import os
import csv
import math
import time
import threading
import pyttsx3
from qr_logic import QRGeneratorLogic

# --- CONFIGURATION ---
THEME = {
    "bg": "#050510",        # Deep Space Black
    "fg": "#00f0ff",        # Cyan / Arc Reactor Blue
    "accent": "#00aaff",    # Slightly darker cyan
    "panel_bg": "#0a0a1a",  # Dark Blue-Grey for panels
    "border": "#00f0ff",    # Glowing border color
    "danger": "#ff3333",    # Red for errors/exit
    "font_main": ("Segoe UI", 10),
    "font_mono": ("Consolas", 10),
    "font_header": ("Segoe UI", 14, "bold"),
    "font_tech": ("Consolas", 12, "bold"),
}

class JarvisButton(tk.Button):
    """Custom Button styled like a HUD element."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=THEME["panel_bg"],
            fg=THEME["fg"],
            activebackground=THEME["fg"],
            activeforeground=THEME["bg"],
            relief=tk.FLAT,
            bd=1,
            font=THEME["font_tech"],
            highlightthickness=1,
            highlightbackground=THEME["border"],
            highlightcolor=THEME["fg"]
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.configure(bg=THEME["accent"], fg=THEME["bg"])

    def on_leave(self, e):
        self.configure(bg=THEME["panel_bg"], fg=THEME["fg"])

class UniversalQRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("J.A.R.V.I.S. QR PROTOCOL")
        self.geometry("1150x800")
        self.configure(bg=THEME["bg"])
        
        # Voice Engine Initialization
        self.voice_enabled = tk.BooleanVar(value=True)
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 170)
            self.engine.setProperty('volume', 0.9)
        except:
            self.voice_enabled.set(False)

        # Variables
        self.content_type = tk.StringVar(value="Website URL")
        self.qr_size = tk.IntVar(value=10)
        self.error_correction = tk.StringVar(value="H")
        self.module_style = tk.StringVar(value="Square")
        self.color_style = tk.StringVar(value="Solid")
        self.fg_color = "#00f0ff"
        self.bg_color = "#000000"
        self.logo_path = tk.StringVar(value="")
        
        # Internal State
        self.current_qr_image = None
        self.current_data = ""
        self.animation_running = True
        self.rotation_angle = 0

        self._setup_styles()
        self._setup_ui()
        self._setup_bindings()
        
        # Start Animation Loop
        self.after(50, self._animate_hud)
        self.speak("J.A.R.V.I.S. online. QR protocol initiated.")

    def speak(self, text):
        """Speaks the text in a separate thread to avoid UI freezing."""
        if self.voice_enabled.get():
            def run_speech():
                try:
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                except: pass
            threading.Thread(target=run_speech, daemon=True).start()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background=THEME["bg"], foreground=THEME["fg"], fieldbackground=THEME["panel_bg"])
        style.map('TCombobox', fieldbackground=[('readonly', THEME["panel_bg"])],
                                selectbackground=[('readonly', THEME["bg"])],
                                selectforeground=[('readonly', THEME["fg"])])
        style.configure("TCombobox", arrowcolor=THEME["fg"], bordercolor=THEME["border"])

    def _setup_ui(self):
        # Header
        header = tk.Frame(self, bg=THEME["bg"], height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        tk.Label(header, text="J.A.R.V.I.S.", font=("Impact", 28), fg=THEME["fg"], bg=THEME["bg"]).pack(side=tk.LEFT)
        tk.Label(header, text=" // QR PROTOCOL INITIATED", font=("Consolas", 14), fg=THEME["accent"], bg=THEME["bg"]).pack(side=tk.LEFT, padx=10, pady=(10, 0))
        
        status_frame = tk.Frame(header, bg=THEME["bg"])
        status_frame.pack(side=tk.RIGHT)
        self.lbl_clock = tk.Label(status_frame, text="00:00:00", font=("Consolas", 12), fg=THEME["fg"], bg=THEME["bg"])
        self.lbl_clock.pack(anchor="e")
        
        # Voice Toggle
        self.chk_voice = tk.Checkbutton(status_frame, text="VOICE_COMMS", variable=self.voice_enabled,
                                        bg=THEME["bg"], fg=THEME["accent"], selectcolor=THEME["bg"],
                                        activebackground=THEME["bg"], activeforeground=THEME["fg"],
                                        font=("Consolas", 8))
        self.chk_voice.pack(anchor="e")

        # Main Content
        main_grid = tk.Frame(self, bg=THEME["bg"])
        main_grid.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # Left Panel
        left_panel = tk.LabelFrame(main_grid, text=" COMMAND INTERFACE ", font=THEME["font_tech"], bg=THEME["bg"], fg=THEME["fg"], bd=2, relief=tk.GROOVE)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left_panel, text="DATA TYPE:", font=THEME["font_mono"], bg=THEME["bg"], fg=THEME["accent"]).pack(anchor="w", padx=10, pady=(10, 0))
        self.cb_type = ttk.Combobox(left_panel, textvariable=self.content_type, state="readonly", values=["Website URL", "Text", "WiFi", "Email", "vCard", "Code"])
        self.cb_type.pack(fill=tk.X, padx=10, pady=5)
        self.cb_type.bind("<<ComboboxSelected>>", self._on_type_change)

        tk.Label(left_panel, text="INPUT STREAM:", font=THEME["font_mono"], bg=THEME["bg"], fg=THEME["accent"]).pack(anchor="w", padx=10, pady=(10, 0))
        self.text_input = tk.Text(left_panel, height=6, font=("Consolas", 11), bg=THEME["panel_bg"], fg=THEME["fg"], insertbackground=THEME["fg"], relief=tk.FLAT)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Configuration Panel
        cfg_frame = tk.LabelFrame(left_panel, text=" SCAN PARAMETERS ", font=THEME["font_mono"], bg=THEME["bg"], fg=THEME["fg"], bd=1)
        cfg_frame.pack(fill=tk.X, padx=10, pady=10)

        # Row 1: Size
        tk.Label(cfg_frame, text="SIZE:", bg=THEME["bg"], fg=THEME["fg"]).grid(row=0, column=0, sticky="w", padx=5)
        tk.Scale(cfg_frame, from_=1, to=20, orient=tk.HORIZONTAL, variable=self.qr_size, bg=THEME["bg"], fg=THEME["fg"], highlightthickness=0, command=lambda x: self.update_preview()).grid(row=0, column=1, sticky="we")

        # Row 2: Module and Color Style
        tk.Label(cfg_frame, text="MODULE:", bg=THEME["bg"], fg=THEME["fg"]).grid(row=1, column=0, sticky="w", padx=5)
        self.cb_module = ttk.Combobox(cfg_frame, textvariable=self.module_style, state="readonly", values=["Square", "Rounded", "Circle", "Gapped", "Vertical", "Horizontal"], width=10)
        self.cb_module.grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(cfg_frame, text="COLOR:", bg=THEME["bg"], fg=THEME["fg"]).grid(row=2, column=0, sticky="w", padx=5)
        self.cb_color_style = ttk.Combobox(cfg_frame, textvariable=self.color_style, state="readonly", values=["Solid", "Radial", "Vertical", "Horizontal"], width=10)
        self.cb_color_style.grid(row=2, column=1, sticky="w", pady=5)

        # Row 3: Colors
        color_btn_frame = tk.Frame(cfg_frame, bg=THEME["bg"])
        color_btn_frame.grid(row=3, column=0, columnspan=2, pady=5)
        JarvisButton(color_btn_frame, text="FOREGROUND", command=self._pick_fg, width=12).pack(side=tk.LEFT, padx=5)
        JarvisButton(color_btn_frame, text="BACKGROUND", command=self._pick_bg, width=12).pack(side=tk.LEFT, padx=5)

        # Row 4: Logo Controls
        logo_btn_frame = tk.Frame(cfg_frame, bg=THEME["bg"])
        logo_btn_frame.grid(row=4, column=0, columnspan=2, sticky="we", padx=5, pady=2)
        JarvisButton(logo_btn_frame, text="ADD LOGO", command=self._browse_logo, width=12).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        JarvisButton(logo_btn_frame, text="REMOVE LOGO", command=self._remove_logo, width=12).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        # Actions
        act_frame = tk.Frame(left_panel, bg=THEME["bg"], pady=10)
        act_frame.pack(fill=tk.X, padx=10)
        JarvisButton(act_frame, text="SAVE ARTIFACT", command=self._save_qr).pack(fill=tk.X, pady=2)
        JarvisButton(act_frame, text="COPY TO CLIPBOARD", command=self._copy_qr).pack(fill=tk.X, pady=2)
        JarvisButton(act_frame, text="CLEAR BUFFER", command=self._clear_input).pack(fill=tk.X, pady=2)

        # Right Panel
        right_panel = tk.Frame(main_grid, bg=THEME["bg"])
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.hud_canvas = tk.Canvas(right_panel, width=550, height=550, bg="#000000", highlightthickness=0)
        self.hud_canvas.pack(expand=True)

        main_grid.columnconfigure(0, weight=1)
        main_grid.columnconfigure(1, weight=2)
        main_grid.rowconfigure(0, weight=1)

    def _setup_bindings(self):
        self.text_input.bind("<KeyRelease>", lambda e: self.update_preview())
        self.cb_module.bind("<<ComboboxSelected>>", lambda e: self.update_preview())
        self.cb_color_style.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

    def _pick_fg(self):
        color = colorchooser.askcolor(title="SELECT FOREGROUND COLOR", initialcolor=self.fg_color)
        if color[1]:
            self.fg_color = color[1]
            self.speak("Foreground color updated.")
            self.update_preview()

    def _pick_bg(self):
        color = colorchooser.askcolor(title="SELECT BACKGROUND COLOR", initialcolor=self.bg_color)
        if color[1]:
            self.bg_color = color[1]
            self.speak("Background color updated.")
            self.update_preview()

    def _draw_hud_elements(self):
        w, h = 550, 550
        cx, cy = w // 2, h // 2
        self.hud_canvas.delete("all")
        for i in range(0, w, 50):
            self.hud_canvas.create_line(i, 0, i, h, fill="#0a0a1a", width=1)
            self.hud_canvas.create_line(0, i, w, i, fill="#0a0a1a", width=1)
        if self.current_qr_image:
            preview_size = 300
            display_img = self.current_qr_image.resize((preview_size, preview_size), Image.NEAREST)
            self.tk_img = ImageTk.PhotoImage(display_img)
            self.hud_canvas.create_image(cx, cy, image=self.tk_img)
            offset = preview_size // 2 + 5
            self.hud_canvas.create_rectangle(cx-offset, cy-offset, cx+offset, cy+offset, outline=self.fg_color, width=1)
        angle = self.rotation_angle
        self.hud_canvas.create_arc(cx-220, cy-220, cx+220, cy+220, start=angle, extent=60, style=tk.ARC, outline=THEME["fg"], width=2)
        self.hud_canvas.create_arc(cx-220, cy-220, cx+220, cy+220, start=angle+120, extent=60, style=tk.ARC, outline=THEME["fg"], width=2)
        self.hud_canvas.create_arc(cx-220, cy-220, cx+220, cy+220, start=angle+240, extent=60, style=tk.ARC, outline=THEME["fg"], width=2)
        self.hud_canvas.create_oval(cx-250, cy-250, cx+250, cy+250, outline="#002233", width=1)

    def _animate_hud(self):
        self.rotation_angle = (self.rotation_angle + 2) % 360
        self.lbl_clock.config(text=time.strftime("%H:%M:%S"))
        self._draw_hud_elements()
        if self.animation_running: self.after(50, self._animate_hud)

    def _remove_logo(self):
        self.logo_path.set("")
        self.speak("Logo overlay removed.")
        self.update_preview()

    def _on_type_change(self, event=None):
        t = self.content_type.get()
        self.text_input.delete("1.0", tk.END)
        if t == "WiFi": self.text_input.insert("1.0", "SSID: MyNetwork\nPassword: MyPassword\nSecurity: WPA")
        elif t == "vCard": self.text_input.insert("1.0", "Name: Tony Stark\nPhone: +1 555 123 4567\nEmail: tony@starkindustries.com\nOrg: Stark Industries\nTitle: CEO")
        elif t == "Website URL": self.text_input.insert("1.0", "https://")
        self.speak(f"{t} template loaded.")
        self.update_preview()

    def _browse_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.logo_path.set(path)
            self.speak("Logo artifact loaded.")
            self.update_preview()

    def _get_input_data(self):
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text: return ""
        ctype = self.content_type.get()
        if ctype in ["WiFi", "Email", "vCard"]:
            data_dict = {}
            for line in raw_text.split('\n'):
                if ':' in line:
                    p = line.split(':', 1)
                    data_dict[p[0].strip().lower()] = p[1].strip()
            if ctype == "WiFi": return QRGeneratorLogic.format_wifi_data(data_dict.get('ssid',''), data_dict.get('password',''), data_dict.get('security','WPA'))
            if ctype == "vCard": return QRGeneratorLogic.format_vcard(data_dict.get('name',''), data_dict.get('phone',''), data_dict.get('email',''), data_dict.get('org',''), data_dict.get('title',''), data_dict.get('url',''))
        return raw_text

    def update_preview(self, event=None):
        data = self._get_input_data()
        self.current_data = data
        if not data: self.current_qr_image = None; return
        try:
            self.current_qr_image = QRGeneratorLogic.generate_qr(
                data, 
                box_size=self.qr_size.get(), 
                fill_color=self.fg_color, 
                back_color=self.bg_color,
                module_style=self.module_style.get(),
                color_style=self.color_style.get(),
                logo_path=self.logo_path.get()
            )
        except Exception as e: print(f"Render Error: {e}")

    def _save_qr(self):
        if not self.current_qr_image: return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if path:
            self.current_qr_image.save(path)
            self.speak("Artifact saved successfully.")

    def _copy_qr(self):
        if not self.current_qr_image: return
        try:
            import win32clipboard
            from io import BytesIO
            output = BytesIO()
            self.current_qr_image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            self.speak("Artifact copied to clipboard.")
        except: pass

    def _clear_input(self):
        self.text_input.delete("1.0", tk.END)
        self.logo_path.set("")
        self.speak("System buffer cleared.")
        self.update_preview()

if __name__ == "__main__":
    app = UniversalQRApp()
    app.mainloop()
