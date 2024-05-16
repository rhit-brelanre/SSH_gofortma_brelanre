# **SSH_gofortma_brelanre**

## **Remote Execution and Monitoring Tool**

### **Project Goal**

Our project's primary objective is to create a remote execution and monitoring software with the following capabilities:

- Establish a secure SSH-like connection for executing commands on a remote machine.
- Return the output of the executed commands back to the server.

## **Version 1: Client-Server Model**

### **Features**

- **Separate Client and Server Files:** The system is split into two distinct files - one for the client and one for the server.
- **Encryption:** Utilizes encryption to secure messages between the client and server.
- **Public and Private Keys:** Each file generates its own private and public keys.
- **Key Exchange:** Public keys are exchanged and used for encryption, while private keys are used for decryption.
- **Command Execution:** Uses the subprocess module to execute commands on the client machine.
- **Encrypted Output:** The output from the executed commands is encrypted and sent back to the server.

### **Workflow**

1. The server and client establish a connection and exchange public keys.
2. The server sends an encrypted command to the client.
3. The client decrypts the command using its private key and executes it using the subprocess module.
4. The command's output is encrypted and sent back to the server.

## **Version 2: Single-File Terminal Emulator**

### **Features**

- **Single File:** The entire functionality is encapsulated in one file, which communicates with the client directly.
- **Terminal Emulator:** Acts as a terminal emulator, allowing remote command execution on the client machine.
- **Custom Commands:** Includes custom commands for monitoring system usage and other shortcuts.
- **Command Logging:** Maintains a log of all commands executed on the machine.
- **Stealth Mode:** Operates without leaving traces that it is currently in the system.

### **Workflow**

1. The server connects to the client and initiates a terminal emulation session.
2. Commands are executed remotely, with special commands available for system monitoring.
3. The system logs all commands executed but does not log its presence on the client machine.

## **Pivot Reasoning**

We initially developed version 1, which utilized a traditional client-server model. However, we encountered several limitations:

- **Client-Side Actions:** Remote execution typically involves server-side actions only.
- **Client Dependency:** Version 1 required the client to run a program and establish a connection to the server.
- **Command Visibility:** All commands were executed by the client, making it possible for the client to see what commands were being run.

To address these limitations, we pivoted to version 2, which streamlined the process by:

- **Single Server File:** Eliminating the need for a separate client program.
- **Enhanced Stealth:** Ensuring that the tool operates without leaving traces on the client machine.

## **Conclusion**

Our remote execution and monitoring tool provides a robust solution for executing commands on a remote machine securely and efficiently. Version 1 laid the groundwork with a client-server model, while version 2 refined the approach with a single-file terminal emulator, offering a more seamless and stealthy operation.

We welcome feedback and contributions to further enhance the functionality and security of our tool.

## **Installation and Usage**

### **Version 1**

### **Server Setup:**

1. Generate public and private keys.
2. Exchange public keys with the client.
3. Run the server script to start listening for connections.

### **Client Setup:**

1. Generate public and private keys.
2. Exchange public keys with the server.
3. Run the client script to connect to the server.

### **Version 2**

#### **Setup:**

- Ensure the server script is configured to connect to the client machine.

#### **Execution:**

1. Run the server script to start the terminal emulation session.
2. Execute commands remotely and utilize custom commands for monitoring.