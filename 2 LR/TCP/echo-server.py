import socket

'''AF_INET is the Internet address family for IPv4. 
   SOCK_STREAM is the socket type for TCP,
   the protocol that will be used to transport messages in the network.'''

HOST = "127.0.0.1"  # localhost
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    #The .bind() method is used to associate the socket with a specific network interface and port number
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            print(f"Message from client: {data}")
            if not data:
                break
            conn.sendall(data)