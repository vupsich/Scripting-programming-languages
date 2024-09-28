import socket

HOST = "127.0.0.1" 
PORT = 65432  

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b"Hello", (HOST, PORT))

    data, server = s.recvfrom(1024)  
    print(f"Received {data!r} from {server}")

    s.sendto(b"Exit", (HOST, PORT))