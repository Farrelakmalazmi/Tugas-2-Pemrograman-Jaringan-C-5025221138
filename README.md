# Tugas 2 Pemrograman Jaringan C 5025221138

## Time Server TCP dengan Multithreading


### Farrel Akmalazmi Nugraha
### 5025221138
---

## Deskripsi Tugas

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

## Demonstrasi Eksekusi

Berikut adalah bukti eksekusi program yang menunjukkan interaksi antara server di `mesin-1` dan klien (`telnet`) di `mesin-2`.

#### 1. Sesi Interaksi Klien (`mesin-2`)
Klien berhasil terhubung ke server dan melakukan beberapa permintaan `TIME` sebelum akhirnya keluar dengan perintah `QUIT`.

```bash
(base) jovyan@272794a38dc5:~/work$ telnet 172.16.16.101 45000
Trying 172.16.16.101...
Connected to 172.16.16.101.
Escape character is '^]'.
TIME
JAM 06:14:20
TIME
JAM 06:14:37
TIME
JAM 06:14:50
QUIT
Connection closed by foreign host.
(base) jovyan@272794a38dc5:~/work$
```

#### 2. Log Aktivitas di Server (`mesin-1`)
Log server mencatat setiap aktivitas secara detail, mulai dari koneksi baru hingga setiap pesan yang diterima dan waktu respons yang dikirim.

```log
2025-06-09 06:14:12,654 - [SERVER] - Server aktif dan mendengarkan di port 45000...
2025-06-09 06:14:16,771 - [SERVER] - Menerima koneksi baru dari ('172.16.16.102', 40036)
2025-06-09 06:14:16,771 - [SERVER] - Thread baru untuk klien ('172.16.16.102', 40036) dimulai.
2025-06-09 06:14:20,355 - [SERVER] - Menerima pesan dari ('172.16.16.102', 40036): 'TIME'
2025-06-09 06:14:20,356 - [SERVER] - Mengirim waktu '06:14:20' ke ('172.16.16.102', 40036)
2025-06-09 06:14:37,430 - [SERVER] - Menerima pesan dari ('172.16.16.102', 40036): 'TIME'
2025-06-09 06:14:37,430 - [SERVER] - Mengirim waktu '06:14:37' ke ('172.16.16.102', 40036)
2025-06-09 06:14:50,924 - [SERVER] - Menerima pesan dari ('172.16.16.102', 40036): 'TIME'
2025-06-09 06:14:50,924 - [SERVER] - Mengirim waktu '06:14:50' ke ('172.16.16.102', 40036)
2025-06-09 06:14:55,348 - [SERVER] - Menerima pesan dari ('172.16.16.102', 40036): 'QUIT'
2025-06-09 06:14:55,348 - [SERVER] - Klien ('172.16.16.102', 40036) meminta keluar. Koneksi ditutup.
2025-06-09 06:14:55,348 - [SERVER] - Thread untuk klien ('172.16.16.102', 40036) telah berhenti.
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
                # Menerima data dari klien, buffer size 1024 bytes sudah cukup.
                data = self.connection.recv(1024)
                if not data:
                    # Jika data kosong, berarti klien menutup koneksi secara tiba-tiba.
                    logging.warning(f"Klien {self.address} menutup koneksi tanpa perintah QUIT.")
                    break

                # Decode data dari bytes ke string (UTF-8) dan hapus spasi/baris baru (\r\n).
                request_str = data.decode('utf-8').strip()
                logging.info(f"Menerima pesan dari {self.address}: '{request_str}'")

                # Memproses permintaan klien berdasarkan protokol yang ditentukan.
                if request_str == "TIME":
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    
                    # Membuat respons sesuai format: "JAM <jam>\r\n"
                    # \r\n (CRLF) adalah penanda akhir pesan yang penting.
                    response = f"JAM {current_time}\r\n"
                    
                    self.connection.sendall(response.encode('utf-8'))
                    logging.info(f"Mengirim waktu '{current_time}' ke {self.address}")
                
                elif request_str == "QUIT":
                    # Jika klien mengirim QUIT, server menutup koneksi dengan rapi.
                    logging.info(f"Klien {self.address} meminta keluar. Koneksi ditutup.")
                    break
                
                else:
                    # Menangani perintah yang tidak valid.
                    error_msg = "PERINTAH TIDAK DIKENALI. Gunakan TIME atau QUIT.\r\n"
                    self.connection.sendall(error_msg.encode('utf-8'))
                    logging.warning(f"Perintah tidak valid dari {self.address}.")

        except ConnectionResetError:
            logging.error(f"Koneksi dengan {self.address} terputus secara paksa oleh klien.")
        finally:
            # Pastikan koneksi ditutup saat loop berakhir.
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
        # Opsi ini memungkinkan server untuk menggunakan kembali alamat port yang sama segera setelah ditutup.
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        # Bind socket ke semua antarmuka jaringan ('0.0.0.0') pada port 45000.
        self.my_socket.bind(('0.0.0.0', self.port))
        self.my_socket.listen(5) # Mampu menampung hingga 5 koneksi dalam antrian.
        logging.info(f"Server aktif dan mendengarkan di port {self.port}...")

        while True:
            # Menerima koneksi baru. Baris ini akan 'memblokir' sampai ada klien yang masuk.
            connection, client_address = self.my_socket.accept()
            logging.info(f"Menerima koneksi baru dari {client_address}")
            
            # Buat dan mulai thread baru untuk menangani klien ini.
            client_thread = ProcessTheClient(connection, client_address)
            client_thread.start()

def main():
    # Menentukan port sesuai tugas
    PORT = 45000
    # Membuat dan memulai server
    server = Server(PORT)
    server.start()

if __name__ == "__main__":
    main()
