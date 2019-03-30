#include <stdlib.h>
#include <string.h>
#include "requestor.h"

int init_requestor(struct requestor *rq, const char* name,
                    int port, const char* ip){

    rq->name = malloc( sizeof(char) * MAX_REQUESTOR_NAME);
    strcpy(rq->name, name);

    rq->port = port;

    rq->ip = malloc( sizeof(char) * IP_LENGTH);
    strcpy(rq->ip, ip);

    rq->id = 0;
    rq->lock = 0;

}

int free_requestor(struct requestor *rq){
    free(rq->name);
    free(rq->ip);
}
