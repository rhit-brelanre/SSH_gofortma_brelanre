import socket
import sys
import threading
import subprocess

import rsa
from Crypto.Cipher import PKCS1_OAEP

COMMAND = 1
EXIT = -1


# takes a connection, performs the communications necessary to authenticate, and returns the public key corresponding to that client
def authenticate_client(conn, public_key):
    # Receive the client's public key
    encrypt_key = recv_msg(conn)

    send_resp(conn, public_key)
    # Perform authentication process here
    # NOTE: For now, just accept any public key and return it

    
    # Return the public key
    return encrypt_key

# takes an encrypted message and a key and returns the decrypted message
def decrypt(msg, key):
    rsa_key = RSA.import_key(key)
    cipher = PKCS1_OAEP.new(rsa_key)
    decrypted_msg = cipher.decrypt(msg)
    return decrypted_msg

# takes a message and a key and encrypts the message

# NOTE: Uses RSA, we can change the algorithm later if needed
def encrypt(msg, key):
    rsa_key = RSA.import_key(key)
    cipher = PKCS1_OAEP.new(rsa_key)
    encrypted_msg = cipher.encrypt(msg)
    return encrypted_msg    


# receives and returns a message from a connection
def recv_msg(conn):
    pass

# sends a message to a connection
def send_resp(conn, resp):
    pass

# splits a string on a separator but leaves portions inside quotes together (used for commands)
def split_ignore_quotes(str, sep):
    if str.find('"') == -1:
        return str
    else:
        split_str = str.split('"')
        complete_split = []
        i = 1
        for substr in split_str:
            if i%2 == 1:
                complete_split += substr.split(' ')
            else:
                complete_split += '\"' + substr + '\"'
    return complete_split

# executes a command and returns the output
def execute_command(command):
    command_arr = split_ignore_quotes(command, ' ')
    command_resp = subprocess.check_output(command_arr)
    return command_resp

# thread to handle the server's actions
def server_thread(client_socket):
    public_key, private_key = RSA.newkeys(512)
    encrypt_key = authenticate_client(client_socket, public_key)
    while True:
        msg = recv_msg(client_socket)
        decrypted_msg = decrypt(msg, key)
        #do stuff with the message then send a response - add stuff for anything else it needs to do
        if decrypted_msg[0] == COMMAND:
            resp = execute_command(decrypted_msg[1:])
            encrypted_resp = encrypt(resp, private_key)
            send_resp(client_socket, encrypted_resp)
        elif decrypted_msg[0] == EXIT:
            break
    client_socket.close()

# main program to listen and start the threads
def server_program():
    port = 3000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind(('localhost', port))

    server_socket.listen(5)

    while True:
        client_socket, address = server_socket.accept()
        t = threading.Thread(target=server_thread, args=(client_socket,))
        t.start()

if __name__ == '__main__':
    server_program()