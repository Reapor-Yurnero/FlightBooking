#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "service.h"

static int ipc_tx(struct requestor* rq, const char* msg){
    
    sendto(rq->sockfd, (const char *)msg, strlen(msg),
           MSG_DONTROUTE, (const struct sockaddr *) rq->servaddr,
           sizeof(struct sockaddr) );
    printf("Hello message sent.\n");

    return 0;
}

static int ipc_rx(struct requestor* rq, char* recv){
    int n, len;
    n = recvfrom(rq->sockfd, (char *)recv, MAXLINE,
                 MSG_WAITALL, (struct sockaddr *) rq->servaddr,
                 &len);
    
    recv[n] = '\0';
    printf("Server : %s\n", recv);
}

static int base_s1(struct requestor* rq){

    char buffer[MAXLINE];
    const char *hello = "\x01Hello from client";
    ipc_tx(rq, hello);
    ipc_rx(rq, buffer);
    
    return 0;
}

const struct serv_ops base_serv_ops = {
    .s1 = base_s1,
};

int init_service(struct serv* s){
    return 0;
}

int remove_service(struct serv* s){
    return 0;
}
