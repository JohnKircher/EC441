/*****************************************************************************
 * client-c.c
 * Name: John Kircher
 * BU ID: 61489057
 * Email: kircherj@bu.edu
 *****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netdb.h>
#include <netinet/in.h>
#include <errno.h>

#define SEND_BUFFER_SIZE 2048


/* TODO: client()
 * Open socket and send message from stdin.
 * Return 0 on success, non-zero on failure
*/
int client(char *server_ip, char *server_port) {
  // create socket
  int sock = 0;
  if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
  {
    perror("socket failed");
    exit(EXIT_FAILURE);
  }

  // create server address
  struct sockaddr_in serv_addr;
  memset(&serv_addr, '0', sizeof(serv_addr));
  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(atoi(server_port));

  // convert IPv4 and IPv6 addresses from text to binary form
  if(inet_pton(AF_INET, server_ip, &serv_addr.sin_addr)<=0)
  {
    perror("address failed");
    exit(EXIT_FAILURE);
  }

  // connect to server
  if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
  {
    perror("connect failed");
    exit(EXIT_FAILURE);
  }

  // send data
  char buffer[SEND_BUFFER_SIZE];
  //int read_bytes;
  //read_bytes = read(STDIN_FILENO, buffer, SEND_BUFFER_SIZE);
  
  //int i;
  size_t packet;
  //int j;
  while(packet = read(STDIN_FILENO, buffer, 2048)){
    send(sock, buffer, packet, 0);
    memset(buffer, 0, sizeof(buffer));
  }
    // size_t array;
    // for(i = 0; i < packet; i++){
    //   array = array + i;
    // }
    
    //break;
    //for(j = 0; j < array; j++){
    //  send(sock, buffer, j, 0);
    //}
    //break;

  // close socket
  close(sock);

  return 0;
}

/*
 * main()
 * Parse command-line arguments and call client function
*/
int main(int argc, char **argv) {
  char *server_ip;
  char *server_port;

  if (argc != 3) {
    fprintf(stderr, "Usage: ./client-c [server IP] [server port] < [message]\n");
    exit(EXIT_FAILURE);
  }

  server_ip = argv[1];
  server_port = argv[2];
  return client(server_ip, server_port);
}
