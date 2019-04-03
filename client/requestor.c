#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <time.h>
#include "requestor.h"

char* id_plus(struct requestor* rq, int num){
    int id = atoi(rq->id)+num;
    sprintf(rq->id, "%d", id);
    return rq->id;
}

int init_requestor(struct requestor *rq, const char* name,
                    int port, const char* ip, char* serip){

    rq->name = malloc( sizeof(char) * MAX_REQUESTOR_NAME);
    strcpy(rq->name, name);

    rq->sockfd = 0;
    // Creating socket file descriptor
    if ( (rq->sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        perror("socket creation failed");
        return -1;
    }

    rq->servaddr = malloc( sizeof(struct sockaddr_in) );
    rq->cliaddr = malloc( sizeof(struct sockaddr_in) );

    memset(rq->servaddr, 0, sizeof(struct sockaddr_in) );
    memset(rq->servaddr, 0, sizeof(struct sockaddr_in) );

    /* set to default */
    rq->servaddr->sin_family = AF_INET;  // IPv4
    rq->servaddr->sin_port = htons(DEF_SERVER_PORT);
    rq->servaddr->sin_addr.s_addr = inet_addr(serip);

    /* set to default */
    rq->cliaddr->sin_family = AF_INET;
    rq->cliaddr->sin_port = htons(port);
    rq->cliaddr->sin_addr.s_addr = inet_addr(ip);

    /* Bind the socket with the client address */
    if ( bind(rq->sockfd, (const struct sockaddr *)rq->cliaddr,
              sizeof(struct sockaddr) ) < 0 )
    {
        perror("Bind failed");
        free(rq->servaddr);
        free(rq->cliaddr);
        return -1;
    }

    memset(rq->id, 0, MAX_INT_LENGTH);
    rq->id[0] = '0';
    id_plus(rq,(int)time(NULL));
    rq->lock = 0;

}

int free_requestor(struct requestor *rq){
    free(rq->name);
    free(rq->servaddr);
    free(rq->cliaddr);
    close(rq->sockfd);
}
