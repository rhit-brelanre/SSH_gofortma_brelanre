import socket
import sys
import threading
import subprocess

import rsa
import rsa.randnum


BUFFER_SIZE = 4096


def authenticate_client(conn, public_key):
    print("about to send keys")
    encrypt_key = recv_msg(conn).decode()
    print("got encryption key")
    send_resp(conn, .encode())
    print("sent encryption key")
    return encrypt_key

def decrypt(msg, key):
    decrypted_message = rsa.decrypt(msg, key).decode()
    return decrypted_message


def encrypt(msg, key):
    encrypted_message = rsa.encrypt(msg.encode(), key)
    return encrypted_message  


def recv_msg(client_socket):
    response = b''
    while True:
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            break
        response += data

    return response

def send_resp(client_socket, msg):
    client_socket.sendall(msg)

def server_thread(client_socket):
    print("in thread")
    public_key, private_key = rsa.newkeys(512)
    print("generated needed keys")
    print("public key: ", str(public_key))
    print("private key: ", str(private_key))
    encrypt_key = authenticate_client(client_socket, public_key)
    print("succesfully authenticated client")
    while True:
        command = input(" -> ")
        encrypted_command = encrypt(command, encrypt_key)
        send_resp(client_socket, encrypted_command)

        if command == 'exit':
            break

        response = recv_msg(client_socket)
        decrypted_response = decrypt(response, private_key)
        decrypted_msg = decrypt(msg, key)
    client_socket.close()

def server_program():
    if((len(sys.argv)) != 2):
        print("Usage: python server.py <server port number>")
        sys.exit()
    
    port = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(('localhost', port))

    server_socket.listen(5)

    while True:
        print("connected")
        client_socket, address = server_socket.accept()
        t = threading.Thread(target=server_thread, args=(client_socket,))
        t.start()

if __name__ == '__main__':
    server_program()