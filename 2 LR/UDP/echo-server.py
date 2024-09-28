import socket

'''AF_INET is the Internet address family for IPv4. 
   SOCK_DGRAM is the socket type for UDP,
   the protocol that will be used to transport messages in the network.'''

HOST = "127.0.0.1"  # localhost
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"Connected by {HOST}:{PORT}")

    while True:
        # Принимаем данные и адрес клиента
        data, addr = s.recvfrom(1024)  # Максимальный размер сообщения 1024 байта
        print(f"Сообщение от клиента {addr}: {data.decode()}")
        
        # Отправляем обратно то же сообщение клиенту
        s.sendto(data, addr)