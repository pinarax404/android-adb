from flask import Flask, jsonify
import subprocess
import threading
import re
import time
import os

# Konfigurasi
ADB_RELAY_PORT = 5555

app = Flask(__name__)

# Variabel global untuk menyimpan status tunnel
tunnel_status = {
    "url": "Sedang dimulai, silakan tunggu...",
    "status": "starting",
    "log": []
}

def run_cloudflared():
    """
    Menjalankan proses cloudflared di background dan memantau outputnya.
    """
    global tunnel_status
    try:
        tunnel_status["log"].append("Memulai proses cloudflared...")
        
        # Perintah untuk membuat tunnel TCP ke port lokal
        command = ["cloudflared", "tunnel", "--url", f"tcp://localhost:{ADB_RELAY_PORT}"]
        
        # Gunakan Popen untuk menjalankan di background dan menangkap output
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore',
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        # Baca output baris per baris
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            tunnel_status["log"].append(line)
            
            # Cari URL tunnel dari output menggunakan regex
            match = re.search(r"([a-zA-Z0-9-]+\.trycloudflare\.com)", line)
            if match:
                found_url = match.group(1)
                tunnel_status["url"] = found_url
                tunnel_status["status"] = "connected"
                print(f"\n\n>>> Tunnel Aktif di: {found_url} <<<\n\n")

    except FileNotFoundError:
        error_msg = "Error: Perintah 'cloudflared' tidak ditemukan. Pastikan sudah terinstal dan ada di PATH sistem Anda."
        tunnel_status["url"] = error_msg
        tunnel_status["status"] = "error"
        print(error_msg)
    except Exception as e:
        error_msg = f"Terjadi kesalahan saat menjalankan cloudflared: {e}"
        tunnel_status["url"] = error_msg
        tunnel_status["status"] = "error"
        print(error_msg)

@app.route('/')
def index():
    """Menampilkan status tunnel dalam format JSON."""
    return jsonify(tunnel_status)

if __name__ == '__main__':
    # Jalankan cloudflared di thread terpisah agar tidak memblokir server Flask
    threading.Thread(target=run_cloudflared, daemon=True).start()
    # Jalankan server Flask
    app.run(host='0.0.0.0', port=8080)