#coding: utf-8
from socket import *
import sys

#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client

if len(sys.argv) != 3:
    print("Please enter port number correctly")
    sys.exit()
else:
    serverPort = int(sys.argv[2])
    serverName = str(sys.argv[1])



clientSocket = socket(AF_INET, SOCK_STREAM)
#This line creates the client’s socket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4. The second parameter indicates that the socket is of type SOCK_STREAM,which means it is a TCP socket (rather than a UDP socket, where we use SOCK_DGRAM). 

clientSocket.connect((serverName, serverPort))
#Before the client can send data to the server (or vice versa) using a TCP socket, a TCP connection must first be established between the client and server. The above line initiates the TCP connection between the client and server. The parameter of the connect( ) method is the address of the server side of the connection. After this line of code is executed, the three-way handshake is performed and a TCP connection is established between the client and server.

#asks for username
#log in phase

username = input('Username: ')
username_check = username + " " + "CHECK_USERNAME"
clientSocket.send(username_check.encode())
username_ack = clientSocket.recv(1024).decode()
#asks for password if username was acknowledged 
if username_ack == "ACK":
    print("Username found!")
    password = input('Password: ')

    clientSocket.send(password.encode())
    password_ack = clientSocket.recv(1024).decode()
    
    #if password was not granted
    #asks for re-enter
    while password_ack != "ACK":
        print("Incorrect Password!")
        password = input('Please re-enter password: ')

        clientSocket.send(password.encode())
        password_ack = clientSocket.recv(1024).decode()     

    print("Password granted!") 
else:
    print("Username does not exist!")
    new_password = input("Enter new password: ")
    clientSocket.send(new_password.encode())
    print(new_password)

#enters the site
while 1:
    print("\n")
    print("The following commands are available: CRT: Create Thread, LST: List Threads, MSG: Post Message, DLT: Delete Message, RDT: Read Thread, EDT: Edit Message, UPD: Upload File, DWN: Download File, RMV: Remove Thread, XIT: Exit, SHT: Shutdown Server")
    print("\n")
    command = input('Enter command:')
    
    clientSocket.send(command.encode())
    
    serverMessage = clientSocket.recv(1024).decode()
    #We wait to receive the reply from the server, store it in serverMessage
    if "CRT" in command:
        if serverMessage == "ACK":
            print("Thread created!")
        elif serverMessage == "EXISTING":
            print("Thread already exists!")
        else:
            print("Please enter command correctly!")
    
    elif command == "LST":
        thread_list = serverMessage.split()
        if serverMessage == "NACK" or len(thread_list) == 0:
            print("No active threads!")
        else:          
            for i in thread_list:
                print(i)
    
    elif "MSG" in command:
        if serverMessage == "ACK":
            print("Message posted!")
        elif serverMessage == "NOT EXIST":
            print("Thread does not exist!")
        else:
            print("Invalid command!")
    
    elif "RDT" in command:
        if serverMessage == "NACK":
            print("Invalid command!")
        elif serverMessage == "NOT EXIST":
            print("Thread does not exist!")
        elif len(serverMessage.split()) == 0:
            print("This thread is empty!")
        else:
            print(serverMessage)
    
    elif "EDT" in command:
        if serverMessage == "NACK":
            print("Invalid command!")
        elif serverMessage == "NOT EXIST":
            print("Thread does not exist!")
        elif serverMessage == "INVALID":
            print("This message can not be edited!")
        elif serverMessage == "ACK":
            print("message edited")

    elif "DLT" in command:
        if serverMessage == "NACK":
            print("Invalid command!")
        elif serverMessage == "NOT EXIST":
            print("Thread does not exist!")
        elif serverMessage == "INVALID":
            print("This message can not be deleted!")
        elif serverMessage == "ACK":
            print("message deleted")

    elif "RMV" in command:
        if serverMessage == "NACK":
            print("Invalid command!")
        elif serverMessage == "NOT EXIST":
            print("Thread does not exist!")
        elif serverMessage == "INVALID":
            print("This thread can not be removed!")
        elif serverMessage == "ACK":
            print("thread removed")


    elif command == "XIT":
        print("Logging off!")
        clientSocket.close()
        sys.exit()
    
    elif "SHT" in command:
        if serverMessage == "ACK":
            print("Server is now shutting down!")
            clientSocket.close()
            sys.exit()
        else:
            print("Admin password did not match!")

    else:
        print ('From Server:',serverMessage)
    
    #print what we have received

    

#clientSocket.close()
#and close the socket
