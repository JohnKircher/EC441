###############################################################################
# client-python.py
# Name: John Kircher
# BU ID: 61489057
# Email: kircherj@bu.edu
###############################################################################

import sys
import socket

SEND_BUFFER_SIZE = 2048

def client(server_ip, server_port):
    """TODO: Open socket and send message from sys.stdin"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))
    packet = ""
    while True:
            packet = sys.stdin.read() 
            array = []
            for x in range(0, len(packet), SEND_BUFFER_SIZE):
                array.append(packet[x : x + SEND_BUFFER_SIZE])
            for x in array:
                s.sendall(x)
            
            
            break
    s.close()

def main():
    """Parse command-line arguments and call client function """
    if len(sys.argv) != 3:
        sys.exit(
            "Usage: python client-python.py [Server IP] [Server Port] < [message]")
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    client(server_ip, server_port)


if __name__ == "__main__":
    main()
