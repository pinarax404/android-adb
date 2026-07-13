# Ghost-ADB-ANDROID

![Menu Ghost-ADB](/img/view-adb.png)

_Contoh menu awal Ghost-ADB_

![Perintah Ghost-ADB](/img/Command.png)

**Skript kontrol ADB (Android Debug Bridge) berbasis Bash**

Repositori ini berisi `Ghost-Adb.sh`, sebuah skrip yang
memanfaatkan `adb` untuk mengendalikan dan mengumpulkan data dari
perangkat Android melalui koneksi USB ataupun TCP/IP. Fitur utamanya
termasuk dump SMS, riwayat panggilan, kontak, kontrol kamera dan
layar, hingga operasi sistem lanjutan.

> ⚠️ **Peringatan:** Semua fungsi dalam skrip ini memiliki potensi
> menyalahgunakan privasi. Gunakan hanya untuk pengujian keamanan
> sendiri atau dengan izin pemilik perangkat.

---

## 📌 Persyaratan

- **Sistem Operasi:** Linux (direkomendasikan, cth: Kali, Ubuntu) atau Windows dengan WSL.
- **Python:** Versi 3.8 atau lebih baru.
- **Koneksi:** Kabel USB atau koneksi WiFi di jaringan yang sama dengan perangkat target.

---

## 🧱 Instalasi

Langkah-langkah berikut adalah untuk sistem berbasis Debian/Ubuntu (seperti Kali Linux).

### 1. Clone Repositori
```bash
git clone https://github.com/youruser/Ghost-ADB.git    # Ganti dengan alamat repositori Anda
cd Ghost-ADB
```

### 2. Instal Dependensi Sistem
Paket-paket ini diperlukan untuk fungsionalitas inti dan antarmuka.
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install android-tools-adb scrcpy dialog avahi-daemon -y
```

### 3. Instal Dependensi Python
Aplikasi GUI modern (`GUI_App.py`) memerlukan beberapa paket Python.
```bash
pip install -r requirements.txt
```

> ⚠️ **Catatan untuk Pengguna Linux:** Jika Anda mendapatkan error tentang "externally-managed-environment", ini adalah fitur keamanan baru. Anda bisa mengatasinya dengan menggunakan virtual environment (direkomendasikan) atau dengan menambahkan flag `--break-system-packages`:
> ```bash
> pip install -r requirements.txt --break-system-packages
> ```

### 4. Berikan Izin Eksekusi
Agar skrip-skrip bisa dijalankan:
```bash
chmod +x *.sh
```

---

### Instalasi Cepat (Legacy)
Jika Anda hanya ingin menggunakan skrip Bash (`Ghost-Adb-v1.0.sh`):
   ```bash
   git clone https://github.com/youruser/Ghost-ADB.git    # gunakan alamat repositori Ghost-ADB Anda
   cd Ghost-ADB    # atau direktori tempat skrip berada
   chmod +x Ghost-Adb.sh                                   # berikan izin eksekusi
   ```
4. Jalankan skrip untuk mulai menggunakan:
   ```bash
   ./Ghost-Adb.sh
   ```

### Termux

```bash
pkg update && pkg upgrade -y
pkg install adb termux-api -y
```

Kemudian clone repositori Ghost-ADB:

```bash
git clone https://github.com/youruser/Ghost-ADB.git
cd Ghost-ADB
chmod +x Ghost-Adb.sh
```

Lalu jalankan skrip di dalam Termux.

> Jika mendapat peringatan USB, jalankan:
>
> ```bash
> termux-usb -l
> ```
>
> untuk mendeteksi perangkat.

---

## 🚀 Cara Menggunakan

1. Aktifkan _USB debugging_ pada perangkat Android.
2. Sambungkan via USB atau gunakan pairing TCP/IP (menu 2 atau 6).
3. Jalankan skrip dan pilih opsi dari menu interaktif.
4. Loot (file/hasil dump) tersimpan ke folder `ADB_LOOT` di direktori
   skrip.

Contoh menjalankan (dari direktori skrip atau lewat symlink):

```bash
./Ghost-Adb.sh      # jika berada di folder skrip
# atau, jika sudah membuat symlink di /usr/local/bin:
ghost-adb             # panggil langsung dari PATH
```

Menu utama menampilkan berbagai kemampuan seperti pengambilan
lokasi GPS, dump kontak, kontrol layar, instal/uninstal APK, dan
shell manual.

---

## 🗂️ Struktur Repo

```
Ghost-Adb.sh   # skrip utama
README.md        # dokumentasi ini
.config_adb/     # cache IP & perangkat
ADB_LOOT/        # hasil dump/perintah
```

---

## 📝 Lisensi

Skrip ini dirilis tanpa lisensi formal; gunakan untuk tujuan
edukasi dan riset keamanan. Anda bertanggung jawab atas setiap
penggunaan.

---

## 🤝 Kontribusi

Fork repositori, lakukan perubahan, dan kirim pull request. Tambahkan
fitur, perbaiki bug, atau perjelas dokumentasi.

---

> ### 🔄 Pembaruan Terbaru
>
> - Skrip utama (`Ghost-Adb.sh`) telah diperbarui. Pastikan untuk
>   mengunduh versi terbaru atau menjalankan `git pull` jika Anda
>   menggunakan klon repositori.
> - Perubahan lain disertakan dalam catatan commit.
>
> _Terakhir diperbarui: 12 Maret 2026_

# Hack-Android-RAT
