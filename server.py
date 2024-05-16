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
        session_id = str(uuid.uuid4())  
        with open(f"command_logs/{session_id}.txt", "w") as f:
            f.write(f"Session ID: {session_id}\n")
        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=client_ip, port=client_port, username=username, password=password)
        
        sftp_client = ssh_client.open_sftp()

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
                    if target_directory == '..':
                        current_directory = os.path.dirname(current_directory.rstrip('/'))
                    else:
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
            elif command.lower() == 'upload':
                if len(arguments) < 2:
                    print("Usage: upload <local_file_path> <remote_directory>")
                else:
                    local_file_path = arguments[0]
                    remote_directory = arguments[1]
                    try:
                        sftp_client.put(local_file_path, os.path.join(remote_directory, os.path.basename(local_file_path)))
                        print("File uploaded successfully.")
                    except FileNotFoundError:
                        print("Local file not found.")
                    except IOError:
                        print("Error occurred during file upload.")   
            elif command.lower() == 'download':
                if len(arguments) < 2:
                    print("Usage: download <remote_file_path> <local_directory>")
                else:
                    remote_file_path = arguments[0]
                    local_directory = arguments[1]
                    try:
                        sftp_client.get(remote_file_path, os.path.join(local_directory, os.path.basename(remote_file_path)))
                        print("File downloaded successfully.")
                    except FileNotFoundError:
                        print("Remote file not found.")
                    except IOError:
                        print("Error occurred during file download.")
            elif command.lower() == 'delete':
                if len(arguments) < 1:
                    print("Usage: delete <remote_file_path>")
                else:
                    remote_file_path = arguments[0]
                    try:
                        sftp_client.remove(remote_file_path)
                        print("File deleted successfully.")
                    except FileNotFoundError:
                        print("Remote file not found.")
                    except IOError:
                        print("Error occurred while deleting file.")
            elif command.lower() == 'portscan':
                if len(arguments) < 2:
                    print("Usage: portscan <host> <start_port> <end_port>")
                else:
                    host = arguments[0]
                    start_port = int(arguments[1])
                    end_port = int(arguments[2])
                    try:
                        for port in range(start_port, end_port + 1):
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            result = sock.connect_ex((host, port))
                            if result == 0:
                                print(f"Port {port} is open")
                            sock.close()
                    except KeyboardInterrupt:
                        print("Port scan stopped.")
                    except socket.gaierror:
                        print("Hostname could not be resolved.")
                    except socket.error:
                        print("Could not connect to server.")
            elif command.lower() == 'sysinfo':
                try:
                    success, output = execute_command(ssh_client, 'uname -a', session_id=session_id)
                    if success:
                        print("System Information:")
                        print(output)
                    else:
                        print("Failed to retrieve system information.")
                except Exception as e:
                    print(f"Error retrieving system information: {e}")
            elif command.lower() == 'cpu':
                try:
                    success, output = execute_command(ssh_client, 'top -bn1 | grep "Cpu(s)"', session_id=session_id)
                    if success:
                        print("CPU Usage:")
                        print(output)
                    else:
                        print("Failed to retrieve CPU usage information.")
                except Exception as e:
                    print(f"Error retrieving CPU usage information: {e}")
            elif command.lower() == 'memory':
                try:
                    success, output = execute_command(ssh_client, 'free -m', session_id=session_id)
                    if success:
                        print("Memory Usage:")
                        print(output)
                    else:
                        print("Failed to retrieve memory usage information.")
                except Exception as e:
                    print(f"Error retrieving memory usage information: {e}")
            elif command.lower() == 'disk':
                try:
                    success, output = execute_command(ssh_client, 'df -h', session_id=session_id)
                    if success:
                        print("Disk Usage:")
                        print(output)
                    else:
                        print("Failed to retrieve disk usage information.")
                except Exception as e:
                    print(f"Error retrieving disk usage information: {e}")
            elif command.lower() == 'who':
                try:
                    success, output = execute_command(ssh_client, 'who', session_id=session_id)
                    if success:
                        print("Logged-in Users:")
                        print(output)
                    else:
                        print("Failed to retrieve logged-in user information.")
                except Exception as e:
                    print(f"Error retrieving logged-in user information: {e}")

            elif command.lower() == 'last':
                try:
                    success, output = execute_command(ssh_client, 'last', session_id=session_id)
                    if success:
                        print("Last Logged-in Users:")
                        print(output)
                    else:
                        print("Failed to retrieve last logged-in user information.")
                except Exception as e:
                    print(f"Error retrieving last logged-in user information: {e}")
            elif command.lower() == 'ps':
                try:
                    success, output = execute_command(ssh_client, 'ps aux', session_id=session_id)
                    if success:
                        print("Active Processes:")
                        print(output)
                    else:
                        print("Failed to retrieve active process information.")
                except Exception as e:
                    print(f"Error retrieving active process information: {e}")

            elif command.lower() == 'userscount':
                try:
                    success, output = execute_command(ssh_client, 'who | wc -l', session_id=session_id)
                    if success:
                        print("Number of Logged-in Users:")
                        print(output)
                    else:
                        print("Failed to retrieve the number of logged-in users.")
                except Exception as e:
                    print(f"Error retrieving the number of logged-in users: {e}")
            elif command.lower() == 'update':
                try:
                    success, output = execute_command(ssh_client, 'sudo apt-get update && sudo apt-get upgrade -y', session_id=session_id)
                    if success:
                        print("Software Update Successful.")
                    else:
                        print("Failed to update software.")
                except Exception as e:
                    print(f"Error updating software: {e}")
            elif command.lower() == 'adduser':
                if len(arguments) < 1:
                    print("Usage: adduser <username>")
                else:
                    username = arguments[0]
                    try:
                        success, output = execute_command(ssh_client, f'sudo adduser {username}', session_id=session_id)
                        if success:
                            print(f"User '{username}' added successfully.")
                        else:
                            print(f"Failed to add user '{username}'.")
                    except Exception as e:
                        print(f"Error adding user '{username}': {e}")
            elif command.lower() == 'top':
                try:
                    success, output = execute_command(ssh_client, 'top -n 1', session_id=session_id)
                    if success:
                        print("System Processes (top 10):")
                        print(output)
                    else:
                        print("Failed to retrieve system processes.")
                except Exception as e:
                    print(f"Error retrieving system processes: {e}")

            elif command.lower() == 'tail':
                if len(arguments) < 1:
                    print("Usage: tail <log_file>")
                else:
                    log_file = arguments[0]
                    try:
                        success, output = execute_command(ssh_client, f'tail -n 10 {log_file}', session_id=session_id)
                        if success:
                            print(f"Last 10 lines of '{log_file}':")
                            print(output)
                        else:
                            print(f"Failed to read log file '{log_file}'.")
                    except Exception as e:
                        print(f"Error reading log file '{log_file}': {e}")

            elif command.lower() == 'grep':
                if len(arguments) < 2:
                    print("Usage: grep <pattern> <file>")
                else:
                    pattern = arguments[0]
                    file_path = arguments[1]
                    try:
                        success, output = execute_command(ssh_client, f'grep {pattern} {file_path}', session_id=session_id)
                        if success:
                            print(f"Lines containing '{pattern}' in '{file_path}':")
                            print(output)
                        else:
                            print(f"No matches found for '{pattern}' in '{file_path}'.")
                    except Exception as e:
                        print(f"Error searching for '{pattern}' in '{file_path}': {e}")
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
