###############################################################################
# server-python.py
# Name: John Kircher
# BU ID: 61489057
# Email: kircherj@bu.edu
###############################################################################

import sys
import socket

RECV_BUFFER_SIZE = 2048
QUEUE_LENGTH = 10

def server(server_port):
    """TODO: Listen on socket and print received message to sys.stdout"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", server_port))
    s.listen(QUEUE_LENGTH)
    
    while True:
        data = ""
        conn, addr = s.accept()
        while True:
            packet = conn.recv(RECV_BUFFER_SIZE)
            if not packet:
                break
            data = data + packet
        sys.stdout.write(data)
        sys.stdout.flush()
    conn.close()
    


def main():
    """Parse command-line argument and call server function """
    if len(sys.argv) != 2:
        sys.exit("Usage: python server-python.py [Server Port]")
    server_port = int(sys.argv[1])
    server(server_port)


if __name__ == "__main__":
    main()
