#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <errno.h>
#include "service.h"

static int base_s1(int fd, struct sockaddr_in* to){

    int n, len;
    char buffer[MAXLINE];
    const char *hello = "Hello from client";

    sendto(fd, (const char *)hello, strlen(hello),
           MSG_DONTROUTE, (const struct sockaddr *) to,
           sizeof(struct sockaddr) );
    printf("Hello message sent.\n");

    n = recvfrom(fd, (char *)buffer, MAXLINE,
                 MSG_WAITALL, (struct sockaddr *) to,
                 &len);
    buffer[n] = '\0';
    printf("Server : %s\n", buffer);
    return 0;
}

const struct serv_ops base_serv_ops = {
    .s1 = base_s1,
};

int init_service(struct serv* s){

    s->sockfd = 0;
    // Creating socket file descriptor
    if ( (s->sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        perror("socket creation failed");
        return -EBADFD;
    }

    s->servaddr = malloc( sizeof(struct sockaddr_in) );
    s->cliaddr = malloc( sizeof(struct sockaddr_in) );

    memset(s->servaddr, 0, sizeof(struct sockaddr_in) );
    memset(s->servaddr, 0, sizeof(struct sockaddr_in) );

    /* set to default */
    s->servaddr->sin_family = AF_INET;  // IPv4
    s->servaddr->sin_port = htons(DEF_SERVER_PORT);
    s->servaddr->sin_addr.s_addr = inet_addr("127.0.0.1");

    /* Bind the socket with the server address */
    if ( bind(s->sockfd, (const struct sockaddr *)s->cliaddr,
              sizeof(struct sockaddr) ) < 0 )
    {
        perror("Bind failed");
        free(s->servaddr);
        free(s->cliaddr);
        return -EHOSTUNREACH;
    }

    /* set to default */
    s->cliaddr->sin_family = AF_INET;
    s->cliaddr->sin_port = htons(DEF_CLIENT_PORT);
    s->cliaddr->sin_addr.s_addr = inet_addr("127.0.0.1");

    return 0;
}

int remove_service(struct serv* s){
    free(s->servaddr);
    free(s->cliaddr);
    close(s->sockfd);
    return 0;
}
