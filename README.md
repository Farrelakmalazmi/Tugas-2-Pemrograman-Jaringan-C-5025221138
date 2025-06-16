# Tugas 2: Time Server TCP dengan Multithreading

Repositori ini berisi implementasi dari sebuah *time server* sederhana menggunakan Python, yang dibuat sebagai bagian dari tugas mata kuliah **Praktikum Pemrograman Jaringan (Kelas C)**.

**Disusun oleh:**
- **Nama:** Farrel Akmalazmi Nugraha
- **NRP:** 5025221138

---

## Deskripsi Proyek

Program ini adalah sebuah server TCP yang berjalan di **port 45000**. Tujuan utamanya adalah untuk melayani permintaan waktu dari klien secara bersamaan (*concurrently*) menggunakan arsitektur *multithreading*. Setiap klien yang terhubung akan ditangani oleh sebuah *thread* terpisah, memastikan bahwa server tetap responsif dan tidak terblokir oleh satu koneksi pun.

Server ini mengimplementasikan protokol sederhana berbasis teks:
1.  Klien mengirim `TIME` untuk meminta waktu saat ini.
2.  Server merespons dengan format `JAM hh:mm:ss`.
3.  Klien mengirim `QUIT` untuk mengakhiri sesi.

---

## Arsitektur & Desain

Program ini dibangun dengan dua kelas utama untuk mencapai konkurensi:

-   **`Server` (Class)**: Bertindak sebagai *listener* utama. Tugasnya hanya satu: mendengarkan koneksi masuk di port 45000. Ketika sebuah koneksi diterima, kelas ini tidak memprosesnya, melainkan langsung mendelegasikannya dengan membuat objek baru dari `ProcessTheClient`.
-   **`ProcessTheClient` (Class)**: Merupakan *worker thread*. Setiap instance dari kelas ini berjalan di *thread*-nya sendiri dan bertanggung jawab penuh atas seluruh siklus komunikasi dengan satu klien, mulai dari menerima permintaan hingga mengirim respons dan akhirnya menutup koneksi.

Pendekatan ini memastikan skalabilitas dan responsivitas server yang tinggi.

---

## Pengujian dan Demonstrasi

Berikut adalah bukti eksekusi program yang menunjukkan fungsionalitas server, baik untuk klien tunggal maupun klien simultan.

### 1. Pengujian Klien Tunggal (Dasar)

Pengujian awal dilakukan dengan satu klien untuk memverifikasi fungsionalitas dasar.

**Sesi Interaksi Klien (`mesin-2`):**
```bash
(base) jovyan@272794a38dc5:~/work$ telnet 172.16.16.101 45000
Trying 172.16.16.101...
Connected to 172.16.16.101.
Escape character is '^]'.
TIME
JAM 06:14:20
QUIT
Connection closed by foreign host.
```

**Log Aktivitas di Server (`mesin-1`):**
```log
2025-06-09 06:14:12,654 - [SERVER] - Server aktif dan mendengarkan di port 45000...
2025-06-09 06:14:16,771 - [SERVER] - Menerima koneksi baru dari ('172.16.16.102', 40036)
2025-06-09 06:14:16,771 - [SERVER] - Thread baru untuk klien ('172.16.16.102', 40036) dimulai.
2025-06-09 06:14:20,355 - [SERVER] - Menerima pesan dari ('172.16.16.102', 40036): 'TIME'
2025-06-09 06:14:20,356 - [SERVER] - Mengirim waktu '06:14:20' ke ('172.16.16.102', 40036)
2025-06-09 06:14:55,348 - [SERVER] - Menerima pesan dari ('172.16.16.102', 40036): 'QUIT'
2025-06-09 06:14:55,348 - [SERVER] - Klien ('172.16.16.102', 40036) meminta keluar. Koneksi ditutup.
2025-06-09 06:14:55,348 - [SERVER] - Thread untuk klien ('172.16.16.102', 40036) telah berhenti.
```

### 2. Pengujian Konkurensi (Dua Klien Simultan)

Untuk membuktikan kemampuan *multithreading*, server diuji dengan dua klien yang terhubung secara bersamaan dari `mesin-2` dan `mesin-3`.

**Sesi Interaksi Klien 1 (`mesin-2`):**
```bash
(base) jovyan@272794a38dc5:~/work$ telnet 172.16.16.101 45000
Trying 172.16.16.101...
Connected to 172.16.16.101.
Escape character is '^]'.
TIME
JAM 08:55:11
TIME
JAM 08:55:27
QUIT
Connection closed by foreign host.
```

**Sesi Interaksi Klien 2 (`mesin-3`):**
```bash
(base) jovyan@59f6059766dd:~/work$ telnet 172.16.16.101 45000
Trying 172.16.16.101...
Connected to 172.16.16.101.
Escape character is '^]'.
TIME
JAM 08:55:14
TIME
JAM 08:55:27
QUIT
Connection closed by foreign host.
```

**Log Aktivitas Konkuren di Server (`mesin-1`):**
Log ini secara jelas menunjukkan bagaimana server menangani permintaan dari dua klien (`...102` dan `...103`) secara bergantian tanpa memblokir satu sama lain.
```log
2025-06-16 08:54:40,976 - [SERVER] - Server aktif dan mendengarkan di port 45000...
2025-06-16 08:55:03,200 - [SERVER] - Menerima koneksi baru dari ('172.16.16.103', 34758)
2025-06-16 08:55:03,201 - [SERVER] - Thread baru untuk klien ('172.16.16.103', 34758) dimulai.
2025-06-16 08:55:05,192 - [SERVER] - Menerima koneksi baru dari ('172.16.16.102', 58400)
2025-06-16 08:55:05,193 - [SERVER] - Thread baru untuk klien ('172.16.16.102', 58400) dimulai.
2025-06-16 08:55:11,352 - [SERVER] - Menerima pesan dari ('172.16.16.102', 58400): 'TIME'
2025-06-16 08:55:11,353 - [SERVER] - Mengirim waktu '08:55:11' ke ('172.16.16.102', 58400)
2025-06-16 08:55:14,235 - [SERVER] - Menerima pesan dari ('172.16.16.103', 34758): 'TIME'
2025-06-16 08:55:14,236 - [SERVER] - Mengirim waktu '08:55:14' ke ('172.16.16.103', 34758)
2025-06-16 08:55:27,117 - [SERVER] - Menerima pesan dari ('172.16.16.103', 34758): 'TIME'
2025-06-16 08:55:27,118 - [SERVER] - Mengirim waktu '08:55:27' ke ('172.16.16.103', 34758)
2025-06-16 08:55:27,869 - [SERVER] - Menerima pesan dari ('172.16.16.102', 58400): 'TIME'
2025-06-16 08:55:27,869 - [SERVER] - Mengirim waktu '08:55:27' ke ('172.16.16.102', 58400)
2025-06-16 08:55:32,255 - [SERVER] - Menerima pesan dari ('172.16.16.102', 58400): 'QUIT'
2025-06-16 08:55:32,256 - [SERVER] - Klien ('172.16.16.102', 58400) meminta keluar. Koneksi ditutup.
2025-06-16 08:55:32,256 - [SERVER] - Thread untuk klien ('172.16.16.102', 58400) telah berhenti.
2025-06-16 08:55:36,893 - [SERVER] - Menerima pesan dari ('172.16.16.103', 34758): 'QUIT'
2025-06-16 08:55:36,893 - [SERVER] - Klien ('172.16.16.103', 34758) meminta keluar. Koneksi ditutup.
2025-06-16 08:55:36,894 - [SERVER] - Thread untuk klien ('172.16.16.103', 34758) telah berhenti.
```

---

## Kode Sumber Lengkap (`server_time.py`)

Berikut adalah kode sumber final yang digunakan dalam proyek ini.

```python
import socket
import threading
import logging
from datetime import datetime

# Konfigurasi logging untuk menampilkan informasi secara rapi dengan timestamp.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SERVER] - %(message)s')

class ProcessTheClient(threading.Thread):
    """
    Kelas ini akan menangani setiap koneksi klien dalam thread-nya sendiri.
    Ini adalah kunci untuk membuat server dapat melayani banyak klien secara bersamaan.
    """
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        logging.info(f"Thread baru untuk klien {self.address} dimulai.")
        try:
            while True:
                data = self.connection.recv(1024)
                if not data:
                    logging.warning(f"Klien {self.address} menutup koneksi tanpa perintah QUIT.")
                    break

                request_str = data.decode('utf-8').strip()
                logging.info(f"Menerima pesan dari {self.address}: '{request_str}'")

                if request_str == "TIME":
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    response = f"JAM {current_time}\r\n"
                    self.connection.sendall(response.encode('utf-8'))
                    logging.info(f"Mengirim waktu '{current_time}' ke {self.address}")
                
                elif request_str == "QUIT":
                    logging.info(f"Klien {self.address} meminta keluar. Koneksi ditutup.")
                    break
                
                else:
                    error_msg = "PERINTAH TIDAK DIKENALI. Gunakan TIME atau QUIT.\r\n"
                    self.connection.sendall(error_msg.encode('utf-8'))
                    logging.warning(f"Perintah tidak valid dari {self.address}.")

        except ConnectionResetError:
            logging.error(f"Koneksi dengan {self.address} terputus secara paksa oleh klien.")
        finally:
            self.connection.close()
            logging.info(f"Thread untuk klien {self.address} telah berhenti.")


class Server(threading.Thread):
    """
    Kelas Server utama yang tugasnya hanya mendengarkan koneksi baru
    dan menyerahkannya ke thread ProcessTheClient.
    """
    def __init__(self, port):
        self.port = port
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', self.port))
        self.my_socket.listen(5)
        logging.info(f"Server aktif dan mendengarkan di port {self.port}...")

        while True:
            connection, client_address = self.my_socket.accept()
            logging.info(f"Menerima koneksi baru dari {client_address}")
            
            client_thread = ProcessTheClient(connection, client_address)
            client_thread.start()

def main():
    PORT = 45000
    server = Server(PORT)
    server.start()

if __name__ == "__main__":
    main()
