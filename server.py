import paramiko
import socket

def execute_command(client_ip, client_port, username, password, command):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh_client.connect(hostname=client_ip, port=client_port, username=username, password=password)
        
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if error:
            success = False
            output += "\nError: " + error
        else:
            success = True
        
        return success, output
    except paramiko.AuthenticationException:
        return False, "Authentication failed. Please check your credentials."
    except paramiko.SSHException as ssh_exception:
        return False, f"SSH error: {ssh_exception}"
    except socket.error as socket_error:
        return False, f"Socket error: {socket_error}"
    finally:
        ssh_client.close()

if __name__ == "__main__":
        
        client_ip = input("Enter client IP address: ")
        client_port = input("Enter client port: ")
        username = input("Enter username: ")
        password = input("Enter password: ")
        if(client_ip == ""):
            client_ip = "localhost"
        if(client_port == ""):
            client_port = 22

        if(username == "" or password == ""):
            print("Enter username and password")
            exit()
        

        while True:
            command = input(" > ")

            if command.lower() == 'exit':
                break
            
            success, output = execute_command(client_ip, client_port, username, password, command)
            # if success:
                # print("Command executed successfully:")
            if not success:
                print("Command execution failed:")
            print(output)
