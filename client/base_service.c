#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include "service.h"

int ipc_tx(struct requestor* rq, const char* msg){
    
    sendto(rq->sockfd, (const char *)msg, strlen(msg),
           MSG_DONTROUTE, (const struct sockaddr *) rq->servaddr,
           sizeof(struct sockaddr) );
    printf("Hello message sent.\n");

    return 0;
}

int ipc_rx(struct requestor* rq, char* recv){
    int n, len;
    n = recvfrom(rq->sockfd, (char *)recv, MAXLINE,
                 MSG_WAITALL, (struct sockaddr *) rq->servaddr,
                 &len);
    
    recv[n] = '\0';
    printf("Server : %s\n", recv);
}

char* ipc_cat(char* dest, const char* src){

    int lend = strlen(dest);
    int lens = strlen(src);
    // printf("%d%d",lens,lend);
    dest[lend] = (char) lens;
    dest[lend+1] = '\0';

    return strcat(dest, src);
}

int ipc_concat(int num, char* dest, ...){
 
    va_list valist;
    char* tmp;
 
    va_start(valist, dest);
 
    for (int i = 0; i < num; i++)
    {
       tmp = va_arg(valist, char*);
       ipc_cat(dest,tmp);
    }
    
    va_end(valist);
 
    return 0;
}

static int base_s1(struct requestor* rq){

    char msg[MAXLINE];
    char buffer[MAXLINE];
    char arg1[ARG_LENGTH];
    char arg2[ARG_LENGTH];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("Source city: ");
    scanf("%s",arg1);
    printf("Destination city: ");
    scanf("%s",arg2);

    ipc_concat(6,msg,"0",rq->name,"13","1",arg1,arg2);

    ipc_tx(rq, msg);
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
