#coding: utf-8
from socket import *
import sys
import re
import os.path
#using the socket module

#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client

#Acquires portnumber and admin pass from commandline arguments
if len(sys.argv) != 3:
    print("Please enter port number correctly")
    sys.exit()
else:
    serverPort = int(sys.argv[1])
    admin_password = str(sys.argv[2])
    

serverSocket = socket(AF_INET, SOCK_STREAM)
#This line creates the server’s socket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4.The second parameter indicates that the socket is of type SOCK_STREAM,which means it is a TCP socket (rather than a UDP socket, where we use SOCK_DGRAM).

serverSocket.bind(('localhost', serverPort))
#The above line binds (that is, assigns) the port number 12000 to the server’s socket. In this manner, when anyone sends a packet to port 12000 at the IP address of the server (localhost in this case), that packet will be directed to this socket.

serverSocket.listen(1)
#The serverSocket then goes in the listen state to listen for client connection requests. 

print("The server is ready to receive")



#username to keep track which user
username = ''

#keeping state to check if client has closed connection
alive = False

#function to count lines
def count_lines(fname):
    message_number = -1

    with open('data.txt') as infp:
        for line in infp:
            if line.strip():
                message_number += 1
    
    return message_number

while 1:
    
#When a client knocks on this door, the program invokes the accept( ) method for serverSocket, which creates a new socket in the server, called connectionSocket, dedicated to this particular client. The client and server then complete the handshaking, creating a TCP connection between the client’s clientSocket and the server’s connectionSocket. With the TCP connection established, the client and server can now send bytes to each other over the connection. With TCP, all bytes sent from one side not are not only guaranteed to arrive at the other side but also guaranteed to arrive in order

    if alive == False:
        connectionSocket, addr = serverSocket.accept()
        alive = True

    #receive message from client
    message = connectionSocket.recv(1024).decode()

    #if message contains CHECK_USERNAME tag then it looks for username
    if "CHECK_USERNAME" in message:
        username = message.split()[0]
        print(username)
       #opens the credentials file
        if os.path.isfile("credentials.txt") == False:
            with open("credentials.txt","w") as file:
                pass
        
        with open('credentials.txt','r+') as f:
            
            #checks for username
            #if found, will send an ACK
            if username in f.read():
                connectionSocket.send("ACK".encode())
                print("Username found!")
                
                #if username is found, then waits for password
                pw_ok = False
                while pw_ok == False:
                    password = connectionSocket.recv(1024).decode()
        
                    check_pass = username + " " + password
                    
                    #if password is correct will send an ack
                    #else, sends NACK
                    #waits for new password attempt
                    with open('credentials.txt','r+') as f2:
                        for line in f2:
                            if re.search("{0}$".format(check_pass),line):
                                connectionSocket.send("ACK".encode())
                                print("Password matched!")
                                pw_ok = True

                    if pw_ok == False:
                        connectionSocket.send("NACK".encode())
                        print("Incorrect password!")        
                                

            #if username is not found, sends NACK
            #adds new username and password to the file        
            else:
                connectionSocket.send("NACK".encode())
                password = connectionSocket.recv(1024).decode()
                id_create = username + " " + password
                print("New username!")
                f.write("\n" + id_create)        
    
    #create thread command
    elif "CRT" in message:
        if len(message.split()) != 2 or message.split()[0] != "CRT":
            connectionSocket.send("NACK".encode())
        elif os.path.isfile(message.split()[1] + ".txt"):
            connectionSocket.send("EXISTING".encode())
        else:
            
            with open(message.split()[1] + ".txt", "w+") as thread:
                thread.write(username + "\n")
                connectionSocket.send("ACK".encode())
            with open("threads.txt","a") as thread_list:
                thread_list.write("\n" + message.split()[1])
    
    #list files
    elif message == "LST":
        if os.stat("threads.txt").st_size == 0:
            connectionSocket.send("NACK".encode())
        else:
            with open("threads.txt","r") as thread_list:
                connectionSocket.send(thread_list.read().encode())

    #read thread
    elif "RDT" in message:
        if len(message.split()) != 2 or message.split()[0] != "RDT":
            connectionSocket.send("NACK".encode())
        elif os.path.isfile(message.split()[1] + ".txt") == False:
            connectionSocket.send("NOT EXIST".encode())
        else:
            with open(message.split()[1] + ".txt","r") as thread:
                next(thread)
                connectionSocket.send(thread.read().encode())
    
    #edit a message
    elif "EDT" in message:
        if len(message.split()) < 4 or message.split()[0] != "EDT":
            connectionSocket.send("NACK".encode())
        elif os.path.isfile(message.split()[1] + ".txt") == False:
            connectionSocket.send("NOT EXIST".encode())
        else:
            message_num = message.split()[2]
            data = ''
            prev_line = ''
            valid_req = False
            with open(message.split()[1] + ".txt","r+") as thread_file:
                data = thread_file.read()
                all_lines = data.splitlines()
                for line in all_lines:
                    if (message_num + " " + username + ":") in line:
                        prev_line = line
                        valid_req = True

            edit_message = message_num + " " + username + ":"
            for word in message.split()[3:]:
                edit_message += (" " + word)
            if valid_req == False:
                connectionSocket.send("INVALID".encode())
            else:
                data = data.replace(prev_line, edit_message)
                with open(message.split()[1] + ".txt","wt") as thread_edit:
                    thread_edit.write(data)

            connectionSocket.send("ACK".encode())




    #Remove a thread
    elif "RMV" in message:
        if len(message.split()) != 2 or message.split()[0] != "RMV":
            connectionSocket.send("NACK".encode())
        elif os.path.isfile(message.split()[1] + ".txt") == False:
            connectionSocket.send("NOT EXIST".encode())
        else:
            valid_request = False
            with open(message.split()[1] + ".txt","r") as thread:
                words = thread.read().split()
                if username == words[0]:
                    valid_request = True
            
            if valid_request == True:
                os.remove(message.split()[1] + ".txt")
                with open("threads.txt", "r") as f:
                    lines = f.readlines()
                with open("threads.txt", "w") as f:
                    for line in lines:
                        if line.strip("\n") != message.split()[1]:
                            f.write(line)
                connectionSocket.send("ACK".encode())
            else:
                connectionSocket.send("INVALID".encode())

    elif "MSG" in message:
        if len(message.split()) < 3 or message.split()[0] != "MSG":
            connectionSocket.send("NACK".encode())
        elif os.path.isfile(message.split()[1] + ".txt") == False:
            connectionSocket.send("NOT EXIST".encode())
        else:
            #adds message to thread
            #sends and ACK
            message_number = 0

            with open(message.split()[1] + ".txt") as infp:
                for line in infp:
                    if line.strip():
                        message_number += 1
                #infp.close()
            
            with open(message.split()[1] + ".txt", "a") as thread:
                
                message_number_str = str(message_number) + " "
                post_message = ' '.join(message.split()[2:])
                thread.write("\n" + message_number_str + username + ": " + post_message)
            
            connectionSocket.send("ACK".encode())    
    #deleteing a message
    elif "DLT" in message:
        if len(message.split()) != 3 or message.split()[0] != "DLT":
            connectionSocket.send("NACK".encode())
        elif os.path.isfile(message.split()[1] + ".txt") == False:
            connectionSocket.send("NOT EXIST".encode())
        else:
            message_num = message.split()[2]
            data = ''
            all_lines = []
            valid_req = False
            with open(message.split()[1] + ".txt","r+") as thread_file:
                data = thread_file.read()
                all_lines = data.splitlines()
                for line in all_lines:
                    if (message_num + " " + username + ":") in line:
                        all_lines.remove(line)
                        valid_req = True
            
            if valid_req == True:
                mod_list = []
                for line in all_lines[1:]:
                    if len(line) != 0:
                        words = line.split()
                        m_num = int(message_num)
                        line_num = int(words[0])

                        if line_num > m_num:
                            words[0] = str(line_num - 1)
                            print(words[0])
                            all_lines.remove(line) 
                            line2 = " ".join(words)
                            mod_list.append(line2)
                            print(line)
                for line in mod_list:
                    all_lines.append(line)
                
                print(all_lines)
                data = "\n".join(all_lines)
                with open(message.split()[1] + ".txt","wt") as thread_edit:
                    thread_edit.write(data)
                
                connectionSocket.send("ACK".encode())
            else:
                connectionSocket.send("INVALID".encode())

    #if the message is 'XIT' closes connection with client
    elif message == 'XIT':
        connectionSocket.close()
        alive = False
    #if the message is 'SHT', closes both connection and server socket, and exits.
    elif "SHT" in message:
        if message.split()[1] == admin_password:
            connectionSocket.send("ACK".encode())
            
            if os.path.isfile("threads.txt"):
                with open("threads.txt", "r") as file:
                    data = file.read().split()
                    if len(data) != 0:
                        for n in data:
                            os.remove(n + ".txt")
                
                os.remove("threads.txt")

            os.remove("credentials.txt")
            connectionSocket.close()
            alive = False
            serverSocket.close()
            sys.exit()
        else:
            connectionSocket.send("NACK".encode())

    #Sends a message back
    else:
        connectionSocket.send("Invalid command!".encode())