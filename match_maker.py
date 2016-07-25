import socket
import thread

# containes a match for an alice and a bob...
matches_dict = {}



def client_thread(client_socket):
    tokenRecived = False
    token = ""
    amAlice = False
    while True:
        data = client_socket.recv(4096)

        # We expect the first thing we see the be the match making token on its own,
        # so when we see that we can start throwing data around the place

        print data

        if tokenRecived:
            # Am I alice or bob. If I am alice, send the data to bob

            socket_to_send_to = None
            if amAlice:
                if matches_dict[token].has_key('bob'):
                    socket_to_send_to = matches_dict[token]['bob']
            else:
                socket_to_send_to = matches_dict[token]['alice']

            if socket_to_send_to is not None:
                socket_to_send_to.send(data)
            else:
                print "No friend to send data to"

        else:
            tokenRecived = True
            token = data
            if matches_dict.has_key(token):
                # we've see this token before, so register us with it
                matches_dict[token]['bob'] = client_socket
            else:
                matches_dict[token] = {'alice':client_socket}
                amAlice = True

            print matches_dict




if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM)


    print socket.gethostname()
    server_socket.bind(("127.0.0.1",9913))
    server_socket.listen(5)

    while True:
        (client_socket, address) = server_socket.accept()
        thread.start_new_thread(client_thread,(client_socket,))