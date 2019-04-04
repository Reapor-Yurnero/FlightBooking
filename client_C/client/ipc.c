#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <sys/time.h>
#include "requestor.h"
#include "ipc.h"

int ipc_tx(struct requestor* rq, const char* msg){
    
    sendto(rq->sockfd, (const char *)msg, strlen(msg),
           0, (const struct sockaddr *) rq->servaddr,
           sizeof(struct sockaddr) );

    return 0;
}

int ipc_rx(struct requestor* rq, char* recv){
    int n, len;
    n = recvfrom(rq->sockfd, (char *)recv, MAXLINE,
                 MSG_WAITALL, (struct sockaddr *) rq->servaddr,
                 &len);
    
    recv[n] = '\0';
}

int ipc_rx_wait(struct requestor* rq, char* recv, int timeout){
    int n, len;
    struct timeval tv = {timeout, 0};
    setsockopt(rq->sockfd, SOL_SOCKET, SO_RCVTIMEO, (char*)&tv, sizeof(struct timeval));
    n = recvfrom(rq->sockfd, (char *)recv, MAXLINE,
                 MSG_WAITALL, (struct sockaddr *) rq->servaddr,
                 &len);
    if(n<0){
        return -1;
        // printf("ipc timeout!\n");
    }
    recv[n] = '\0';
    return 0;
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

char* ipc_next_token(char* buffer){
    /* get length */
    int len = (int) *buffer;
    return buffer+len+1;
}

int ipc_disperse(char** tokens,char* buffer){
    /* get end */
    int len_buffer = strlen(buffer);
    char* end = buffer+len_buffer;

    int count=0;
    char* token=buffer;
    tokens[count++]=token+1;
    do{
        token=ipc_next_token(token);
        tokens[count++]=token+1;
    }while(token!=end);

    /* use \0 to separate strings in the buffer */
    for(int i = 1; i < count; i++)
    {
        *(tokens[i]-1)='\0';
    }
    
    return count-1;
}