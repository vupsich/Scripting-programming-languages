import socket

HOST = "127.0.0.1"  # localhost
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"Connected by {HOST}:{PORT}")

    while True:
        
        data, addr = s.recvfrom(1024)  
        print(f"Message from client {addr}: {data.decode()}")
        
        if data.decode() == "Exit":
            print("The server is shutting down")
            break
        
        s.sendto(data, addr)