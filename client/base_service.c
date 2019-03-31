#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "service.h"

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

static int base_s2(struct requestor* rq){
    char msg[MAXLINE];
    char buffer[MAXLINE];
    char arg1[ARG_LENGTH];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("Flight number you want to enquire: ");
    scanf("%s",arg1);

    ipc_concat(5,msg,"0",rq->name,"12","2",arg1);

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);
    
    return 0;
}

static int base_s3(struct requestor* rq){
    char msg[MAXLINE];
    char buffer[MAXLINE];
    char arg1[ARG_LENGTH];
    char arg2[ARG_LENGTH];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("Flight number you want to book: ");
    scanf("%s",arg1);
    printf("Quantity (positive integer): ");
    /* need check here */
    scanf("%s",arg2);

    ipc_concat(6,msg,"0",rq->name,"11","3",arg1,arg2);

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);
    
    return 0;
}


static int base_s4(struct requestor* rq){
    char msg[MAXLINE];
    char buffer[MAXLINE];
    char arg1[ARG_LENGTH];
    char arg2[ARG_LENGTH];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("Flight number you want to monitor: ");
    scanf("%s",arg1);
    printf("How long do you want to monitor? [10, 120] second: ");
    /* need check here */
    scanf("%s",arg2);

    ipc_concat(6,msg,"0",rq->name,"10","4",arg1,arg2);

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);
    
    return 0;
}


static int base_s5(struct requestor* rq){
    char msg[MAXLINE];
    char buffer[MAXLINE];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("wait a second, proceeding...");

    ipc_concat(4,msg,"0",rq->name,"9","5");

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);
    
    return 0;
}


static int base_s6(struct requestor* rq){
    char msg[MAXLINE];
    char buffer[MAXLINE];
    char arg1[ARG_LENGTH];
    char arg2[ARG_LENGTH];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("Flight number you want to cancel: ");
    scanf("%s",arg1);
    printf("Quantity (positive integer): ");
    /* need check here */
    scanf("%s",arg2);

    ipc_concat(6,msg,"0",rq->name,"12","6",arg1,arg2);

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);
    
    return 0;
}

const struct serv_ops base_serv_ops = {
    .s1 = base_s1,
    .s2 = base_s2,
    .s3 = base_s3,
    .s4 = base_s4,
    .s5 = base_s5,
    .s6 = base_s6,
};

static int base_call(int sn, struct requestor* rq){

    struct serv_ops* ops = &base_serv_ops;

    switch (sn)
    {
        case SER_FIND:
            base_s1(rq);
            break;
        case SER_GETDETAIL:
            base_s2(rq);
            break;
        case SER_BOOK:
            base_s3(rq);
            break;
        case SER_MONITOR:
            base_s4(rq);
            break;
        case SER_ORDERINFO:
            base_s5(rq);
            break;
        case SER_CANCEL:
            base_s6(rq);
            break;
        case SER_EXIT:
            break;
        default:
            break;
    }

    return 0;
}

int init_service(struct serv* s){
    s->call_service = base_call;
    return 0;
}

int remove_service(struct serv* s){
    return 0;
}
