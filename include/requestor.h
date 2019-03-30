#ifndef __REQUESTOR_H
#define __REQUESTOR_H

#include <sys/socket.h>
#include <netinet/in.h>
#include "def.h"

#define MAX_REQUESTOR_NAME 30

struct requestor {
    char* name;
    int id;

    int sockfd;
    struct sockaddr_in* servaddr;
    struct sockaddr_in* cliaddr;

    spin_lock_t lock;
};

extern int init_requestor(struct requestor *rq, const char* name,
                    int port, const char* ip);

extern int free_requestor(struct requestor *rq);

#endif /* __REQUESTOR_H */
