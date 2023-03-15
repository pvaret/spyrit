#!/usr/bin/python


import sys
import socket
import random

DEFAULT_FILE = "ansi-telnet-sample.txt"
DEFAULT_PORT = 8000

if __name__ == "__main__":
    try:
        fname = sys.argv[1]
    except IndexError:
        fname = DEFAULT_FILE

    try:
        port = int(sys.argv[2])
    except (IndexError, ValueError):
        port = DEFAULT_PORT

    data = open(fname, "rb").read()

    s = socket.socket()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(("127.0.0.1", port))
    s.listen(5)

    print(
        "Running on port %d. Enter 'stop' in client to stop the server." % port
    )

    while True:
        current = data[:]

        clientsocket, address = s.accept()

        while current:
            sent = clientsocket.send(current[: random.randint(1, 16)])
            current = current[sent:]
            # time.sleep( 0.05 )

        msg = clientsocket.recv(1024)

        clientsocket.shutdown(socket.SHUT_RDWR)
        clientsocket.close()

        if b"stop" in msg.lower():
            break

    s.close()
    print("Server stopped.")
