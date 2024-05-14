import paramiko
import socket
import os

def execute_command(ssh_client, command, arguments=[]):
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
        
        return success, output
    except paramiko.SSHException as ssh_exception:
        return False, f"SSH error: {ssh_exception}"
    except socket.error as socket_error:
        return False, f"Socket error: {socket_error}"

if __name__ == "__main__":
    client_ip = input("Enter client IP address: ")
    client_port = input("Enter client port: ")
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    if client_ip == "":
        client_ip = "localhost"
    if client_port == "":
        client_port = 22

    if username == "" or password == "":
        print("Enter username and password")
        exit()
    
    try:
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
                success, output = execute_command(ssh_client, 'ls', [current_directory])
                if success:
                    print(output)
                else:
                    print("Failed to list directory contents.")
            else:
                success, output = execute_command(ssh_client, command, arguments)
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
