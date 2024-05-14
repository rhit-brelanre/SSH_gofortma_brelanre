# import paramiko
# import socket
# import os
# import threading
# import json
# from getpass import getpass

# def execute_command(ssh_client, command, arguments=[]):
#     try:
#         full_command = command + ' ' + ' '.join(arguments)
        
#         stdin, stdout, stderr = ssh_client.exec_command(full_command)
        
#         output = stdout.read().decode('utf-8')
#         error = stderr.read().decode('utf-8')
        
#         if error:
#             success = False
#             output += "\nError: " + error
#         else:
#             success = True
        
#         return success, output
#     except paramiko.SSHException as ssh_exception:
#         return False, f"SSH error: {ssh_exception}"
#     except socket.error as socket_error:
#         return False, f"Socket error: {socket_error}"
import paramiko
import socket
import os
import threading
import json
from getpass import getpass
import uuid

def execute_command(ssh_client, command, arguments=[], session_id=None):
    try:
        full_command = command + ' ' + ' '.join(arguments)
        
        stdin, stdout, stderr = ssh_client.exec_command(full_command)
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if error:
            success = False
            output += "\nError: " + error
        else:
            success = True
        
        if session_id:
            with open(f"command_logs/{session_id}.txt", "a") as f:
                f.write(f"Command: {full_command}\n")
                f.write("Output:\n")
                f.write(output)
                f.write("\n\n")
        
        return success, output
    except paramiko.SSHException as ssh_exception:
        return False, f"SSH error: {ssh_exception}"
    except socket.error as socket_error:
        return False, f"Socket error: {socket_error}"

def handle_client(client_ip, client_port, username, password):
    try:
        session_id = str(uuid.uuid4())  # Generate a unique session ID
        with open(f"command_logs/{session_id}.txt", "w") as f:
            f.write(f"Session ID: {session_id}\n")
        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=client_ip, port=client_port, username=username, password=password)
        
        current_directory = "/"
        
        while True:
            command_with_args = input(f"{username}@{client_ip}:{current_directory} > ")
            command_parts = command_with_args.split(' ')
            command = command_parts[0]
            arguments = command_parts[1:]
            
            if command.lower() == 'exit':
                break
            elif command.lower() == 'cd':
                if arguments:
                    target_directory = arguments[0]
                    if target_directory.startswith('/'):
                        current_directory = target_directory
                    else:
                        current_directory = os.path.join(current_directory, target_directory)
                else:
                    print("Usage: cd <directory>")
            elif command.lower() == 'pwd':
                print(current_directory)
            elif command.lower() == 'ls':
                success, output = execute_command(ssh_client, 'ls', [current_directory], session_id=session_id)
                if success:
                    print(output)
                else:
                    print("Failed to list directory contents.")
            else:
                success, output = execute_command(ssh_client, command, arguments, session_id=session_id)
                if not success:
                    print("Command execution failed:")
                print(output)
    
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as ssh_exception:
        print(f"SSH error: {ssh_exception}")
    except socket.error as socket_error:
        print(f"Socket error: {socket_error}")
    finally:
        ssh_client.close()

def load_clients():
    try:
        with open("clients.txt", "r") as file:
            file_content = file.read()
            if not file_content:
                print("Clients file is empty.")
                return []
            clients = json.loads(file_content)
            return clients
    except FileNotFoundError:
        print("No previous clients found. Please connect to a client first.")
        exit()
    except json.decoder.JSONDecodeError:
        print("Error: Invalid JSON format in clients file.")
        return []

def save_clients(clients):
    with open("clients.txt", "w") as file:
        json.dump(clients, file)

if __name__ == "__main__":
    
    clients = load_clients()
    if(len(clients) == 0):
        print("No previous clients found. Please connect to a client first.")

    # Ask the user if they want to connect to a previous client or a new client
    choice = input("Do you want to connect to a previous client (P) or a new client (N)? ")

    if choice.lower() == 'p':
        # Display the list of previous clients
            
        print("Previous clients:")
        for i, client in enumerate(clients):
            print(f"{i+1}. Host: {client['client_ip']}, Port: {client['client_port']}, Username: {client['username']}")
        
        # Ask the user to select a previous client
        selection = int(input("Enter the number of the client you want to connect to: "))
        
        # Get the selected client information
        selected_client = clients[selection-1]
        
        # Connect to the selected client
        handle_client(selected_client["client_ip"], selected_client["client_port"], selected_client["username"], selected_client["password"])
    elif choice.lower() == 'n':
        # Ask for information about a new client
        client_ip = input("Enter the client IP: ")
        client_port = int(input("Enter the client port: "))
        username = input("Enter the username: ")
        password = getpass("Enter the password: ")
        
        clients.append({"client_ip": client_ip, "client_port": client_port, "username": username, "password": password})
        save_clients(clients)
        
        # Connect to the new client
        handle_client(client_ip, client_port, username, password)
    else:
        print("Invalid choice. Please try again.")

    threads = []
    for client in clients:
        t = threading.Thread(target=handle_client, args=(client["client_ip"], client["client_port"], client["username"], client["password"]))
        threads.append(t)
        t.start()

    for t in threads:
        t.join() 
