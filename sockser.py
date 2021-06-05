import socket
import select

HEADER_LENGTH = 20

H_IP = "192.168.56.110"
PORT = 1025

# Create a socket
server =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#bind
server.bind(('192.168.56.110', PORT))

#server listen to new connections
server.listen()

# List of sockets for select.select()
socketList = [server]

# List of connected clients - socket as a key, user header and name as data
clients = {}

print(f'{H_IP} is listening to client.....')

# Handles message receiving
def receive_message(client):

    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client.recv(message_length)}

    except:

        #exit by pressing ctrl+c or when receive an empty message
        return False

while True:

    read_sockets, _, exception_sockets = select.select(socketList, [], socketList)


    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client, clientAdd = server.accept()

            # Client should send his name right away, receive it
            user = receive_message(client)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            socketList.append(client)

            # Also save username and username header
            clients[client] = user

            print('Server is connected to {}:{}, username: {}'.format(*clientAdd, user['data'].decode('utf-8')))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Connection from: {H_IP} is  closed'.format(clients[notified_socket]['data'].decode('utf-8')))
                socketList.remove(notified_socket)
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Iterate over connected clients and broadcast message
            for client in clients:

                if client != notified_socket:

                        client.send(user['header'] + user['data'] + message['header'] + message['data'])

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        #Remove socket.socket() from the list
        socketList.remove(notified_socket)

        #Remove users list
        del clients[notified_socket]

