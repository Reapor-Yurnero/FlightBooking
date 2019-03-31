#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include "requestor.h"
#include "ipc.h"

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
