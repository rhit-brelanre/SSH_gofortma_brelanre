import sys
import socket
import rsa

def authenticate_server(client_socket, public_key):

    send_resp(client_socket, public_key)

    encrypt_key = recv_msg(client_socket)

    return encrypt_key

def send_resp(client_socket, message):
    pass

def recv_msg(client_socket):
    pass



def client_program():
    if(len(sys.argv) != 3):
        print("Usage: python client.py <server IP address> <server port number>")
        sys.exit()
    port = sys.argv[2]
    server_ip = socket.gethostbyname(sys.argv[1])

    server_addr = (server_ip, port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    client_socket.connect(server_addr)

    public_key, private_key = RSA.newkeys(512)

    encrypt_key = authenticate_server(client_socket, public_key)

    while True:
        encrypted_command = recv_msg(client_socket)
        decryped_command = decrypt(encrypted_command, )


    client_socket.close()


















if __name__ == '__main__':
    client_program()