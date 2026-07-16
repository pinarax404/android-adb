import os
import tkinter
import customtkinter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
        welcome_label = customtkinter.CTkLabel(
            main_frame,
            text="Welcome to Medusa RAT Android",
            font=customtkinter.CTkFont(size=28, weight="bold"),
            text_color="#FF0000"  # Merah Hacker
        )
        welcome_label.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="s")

        # --- Teks Loading ---
        loading_label = customtkinter.CTkLabel(
            main_frame,
            text="Initializing components...",
            font=customtkinter.CTkFont(size=14),
            text_color="gray80"
        )
        loading_label.grid(row=2, column=0, padx=20, pady=10)
        
        # --- Progress Bar ---
        progressbar = customtkinter.CTkProgressBar(
            main_frame,
            width=300,
            mode="indeterminate",
            progress_color="#FF0000"
        )
        progressbar.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="n")
        progressbar.start()

def show_welcome():
    """
    Membuat dan mengembalikan instance dari WelcomeScreen.
    Aplikasi utama bertanggung jawab untuk mainloop dan menghancurkan jendela ini.
    """
    welcome_app = WelcomeScreen()
    return welcome_app