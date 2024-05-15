import socket
import sys
import threading
import subprocess

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random
import rsa
import math


BUFFER_SIZE = 4096


def authenticate_client(client_socket, public_key):
    encrypt_key = RSA.importKey(client_socket.recv(4096), passphrase=None) 
    client_socket.send(public_key.exportKey(format='PEM', passphrase=None, pkcs=1)) 
    return encrypt_key

def decrypt(msg, key):
    cipher = PKCS1_OAEP.new(key)
    decrypted_msg = cipher.decrypt(msg)
    return decrypted_msg.decode()

def encrypt(msg, key):
    cipher = PKCS1_OAEP.new(key)
    encrypted_msg = cipher.encrypt(msg.encode())
    return encrypted_msg

def recv_msg(client_socket, string_size):
    response = b''
    rounds = math.ceil(string_size/BUFFER_SIZE)
    for _ in range(rounds):
        data = client_socket.recv(BUFFER_SIZE)
        response += data
    return response

def send_resp(client_socket, msg):
    client_socket.sendall(msg)

def server_thread(client_socket):
    # generate private key and corresponding public key
    private_key = RSA.generate(4096)
    public_key = private_key.publickey()     
    # get the key to use for encryption from the client
    encrypt_key = authenticate_client(client_socket, public_key)
    # loop to take command input and communicate with server
    while True:
        command = input(" -> ")

        encrypted_command = encrypt(command, encrypt_key)
        size = len(encrypted_command)
        string_size = str(size).zfill(10)
        client_socket.send(string_size.encode())

        send_resp(client_socket, encrypted_command)

        # break if "exit" is input
        if command == 'exit':
            print('Goodbye')
            break

        string_size = int(client_socket.recv(10).decode())

        response = recv_msg(client_socket, string_size)
        decrypted_response = decrypt(response, private_key)
        print("Output from Client:\n", decrypted_response)
    # close socket on break
    client_socket.close()

def server_program():
    # check user input
    if((len(sys.argv)) != 2):
        print("Usage: python server.py <server port number>")
        sys.exit()
    
    port = int(sys.argv[1])

    # create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(('localhost', port))

    server_socket.listen(5)

    # create client socket
    client_socket, address = server_socket.accept()
    print("Client Connected")
    server_thread(client_socket)

if __name__ == '__main__':
    server_program()