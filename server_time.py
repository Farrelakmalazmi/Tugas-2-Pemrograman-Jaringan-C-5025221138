import socket
import threading
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SERVER] - %(message)s')

class ProcessTheClient(threading.Thread):

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