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

        if data != '':

            if tokenRecived:
                if matches_dict.has_key(token):
                    if matches_dict[token]['state'] == "ACTIVE":

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
                        # not active,
                        print "We are no longer active, close and exit thread"
                        client_socket.close()
                        del matches_dict[token]
                        break
                else:
                    print "Error state... we think the token is recived, but we are not in the dict so we need " \
                          " are probably bob and everything has died. Close and exit thread"
                    client_socket.close()
                    break

            else:
                tokenRecived = True
                token = data
                if matches_dict.has_key(token):
                    # we've see this token before, so register us with it
                    matches_dict[token]['bob'] = client_socket
                    matches_dict[token]['alice'].send(token)
                else:
                    matches_dict[token] = {'alice':client_socket, 'state':"ACTIVE"}
                    amAlice = True

                print matches_dict
        else:
            # data was empty or error
            # Alice closes the sockets for her and bob...
            print "We got a data error or socket close..."
            print matches_dict
            print amAlice
            print tokenRecived
            print token
            if tokenRecived and matches_dict.has_key(token):
                if amAlice:
                    del matches_dict[token]['alice']
                else:
                    del matches_dict[token]['bob']
                matches_dict[token]['state'] = "CLOSING"
            else:
                print "No token, we didn't get going, nothing to do beyond close and exit thread"
            client_socket.close()
            break

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM)


    print socket.gethostname()
    server_socket.bind(("0.0.0.0",9913))
    server_socket.listen(5)

    while True:
        (client_socket, address) = server_socket.accept()
        print client_socket.gettimeout()
        client_socket.settimeout(None)
        print client_socket.gettimeout()


        # clean up all the old threads
        for conn in matches_dict.keys():
            if matches_dict[conn]['state'] == "CLOSING":
                if 'alice' not in matches_dict[conn] and 'bob' not in matches_dict[conn]:
                    print "Removing %s" % (conn,)
                    del matches_dict[conn]

        thread.start_new_thread(client_thread,(client_socket,))