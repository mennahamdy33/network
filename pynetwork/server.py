import socket
import select
import pickle
import model
HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP,PORT))

server_socket.listen()

socket_list = [server_socket]
clients = {}

meanOfNumericalData,modeOfCategoricalData,classifier = model.Model().RandomForestModel()

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
       
        message_length = int(message_header.decode("utf-8").strip())
        message = client_socket.recv(message_length)       
        # if(flag):
        #     message = pickle.loads(message)
        return {"header": message_header, "data": message}
    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
         
            if user is False:
                continue
            data = pickle.loads(user['data'])
            if type(data) == dict:
            
                output = model.predict(data
                                        ,meanOfNumericalData
                                        ,modeOfCategoricalData
                                        ,classifier).predict()
                encodedOutput = output.encode('utf-8')
                print(bytes(f"{len(encodedOutput):<{HEADER_LENGTH}}", 'utf-8'))
                client_socket.send(bytes(f"{len(encodedOutput):<{HEADER_LENGTH}}", 'utf-8')+encodedOutput)

            socket_list.append(client_socket)

            clients[client_socket] = user

            # print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")

        else:
            message = receive_message(notified_socket)
            if message is False:
                # print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                socket_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            # print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
        # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:
        # Remove from list for socket.socket()
        socket_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]
