import socket
import thread

# containes a match for an alice and a bob...
matches_dict = {}



def client_thread(client_socket, address):
    tokenReceived = False
    token = ""
    amAlice = False
    while True:
        data = client_socket.recv(4096)

        # We expect the first thing we see the be the match making token on its own,
        # so when we see that we can start throwing data around the place

        if data != '':

            if tokenReceived:
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
                    print "Error state... we think the token is received, but we are not in the dict so we need " \
                          " are probably bob and everything has died. Close and exit thread"
                    client_socket.close()
                    break

            else:
                tokenReceived = True
                token = data
                if matches_dict.has_key(token):
                    print "Bob (%s) sent token %s" % (address, token)
                    # we've see this token before, so register us with it
                    matches_dict[token]['bob'] = client_socket
                    matches_dict[token]['alice'].send(token)
                else:
                    print "Alice (%s) sent token %s" % (address, token)
                    matches_dict[token] = {'alice':client_socket, 'state':"ACTIVE"}
                    amAlice = True

                print matches_dict
        else:
            # data was empty or error
            # Alice closes the sockets for her and bob...
            if tokenReceived and matches_dict.has_key(token):
                if amAlice:
                    print "Alice got a data error or socket close for token '%s'..." % (token)
                    del matches_dict[token]['alice']
                else:
                    print "Bob got a data error or socket close for token '%s'..." % (token)
                    del matches_dict[token]['bob']
                matches_dict[token]['state'] = "CLOSING"
            else:
                print "We got a data error or socket close. No token, just close and exit thread."
            print matches_dict
            client_socket.close()
            break

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM)


    print socket.gethostname()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0",9913))
    server_socket.listen(5)

    while True:
        (client_socket, address) = server_socket.accept()
        print "Socket timeout before setting to None: " + str(client_socket.gettimeout())
        client_socket.settimeout(None)
        print "Socket timeout after setting to None: " + str(client_socket.gettimeout())


        # clean up all the old threads
        for conn in matches_dict.keys():
            if matches_dict[conn]['state'] == "CLOSING":
                if 'alice' not in matches_dict[conn] and 'bob' not in matches_dict[conn]:
                    print "Removing %s" % (conn,)
                    del matches_dict[conn]

        thread.start_new_thread(client_thread,(client_socket, address))
