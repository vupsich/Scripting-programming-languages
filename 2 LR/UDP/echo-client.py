import socket

HOST = "127.0.0.1"  # IP-адрес сервера
PORT = 65432  # Порт, используемый сервером

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    # Отправляем сообщение на сервер
    s.sendto(b"Hello", (HOST, PORT))

    # Получаем ответ от сервера
    data, server = s.recvfrom(1024)  # Максимальный размер сообщения 1024 байта

print(f"Received {data!r} from {server}")