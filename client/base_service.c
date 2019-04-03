#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "service.h"
#include "ipc.h"

static int base_s1(struct requestor* rq){

    char msg[MAXLINE];
    char buffer[MAXLINE];
    char arg1[ARG_LENGTH];
    char arg2[ARG_LENGTH];
    char* tokens[MAX_TOKEN];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("Source city: ");
    scanf("%s",arg1);
    printf("Destination city: ");
    scanf("%s",arg2);

    ipc_concat(6,msg,"0",rq->name,id_plus(rq,1),"1",arg1,arg2);

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);

    int num = ipc_disperse(tokens,buffer);
    if( num > 2 ){
        printf("There is(are) %d flight(s) applicable:\n",num-2);
        for(int i=2; i<num; i++)printf("%s\n",tokens[i]);
    }
    else{
        printf("There is no flight applicable\n");
    }

    return 0;
}

static int base_s2(struct requestor* rq){
    char msg[MAXLINE];
    char buffer[MAXLINE];
    char arg1[ARG_LENGTH];
    char* tokens[MAX_TOKEN];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("Flight number you want to enquire: ");
    scanf("%s",arg1);

    ipc_concat(5,msg,"0",rq->name,id_plus(rq,1),"2",arg1);

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);

    ipc_disperse(tokens,buffer);

    char stime[10];
    if(!strcmp(tokens[1],"0")){
        printf("No such flight!\n"); 
    }
    else{
        strcpy(stime,tokens[2]);
        stime[2]=':';
        strcpy(stime+3,tokens[2]+2);
        printf("Flight will depart at %s, with airfare %s and %s vacancies\n",
            stime,tokens[3],tokens[4]);
    }
    
    return 0;
}

static int base_s3(struct requestor* rq){
    char msg[MAXLINE];
    char buffer[MAXLINE];
    char arg1[ARG_LENGTH];
    char arg2[ARG_LENGTH];
    char* tokens[MAX_TOKEN];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("Flight number you want to book: ");
    scanf("%s",arg1);
    printf("Quantity (positive integer): ");
    /* need check here */
    scanf("%s",arg2);

    ipc_concat(6,msg,"0",rq->name,id_plus(rq,1),"3",arg1,arg2);

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);

    ipc_disperse(tokens,buffer);

    switch (*tokens[1])
    {
        case '1':
            printf("Booked successfully!\n");
            break;
        case '0':
            printf("Not enough vacancy!\n");
            break;
        case '-':
            printf("No such flight!\n");
            break;
        default:
            printf("ipc error!\n");
            return -1;
    }
    
    return 0;
}


static int base_s4(struct requestor* rq){
    char msg[MAXLINE];
    char buffer[MAXLINE];
    char arg1[ARG_LENGTH];
    char arg2[ARG_LENGTH];
    char* tokens[MAX_TOKEN];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("Flight number you want to monitor: ");
    scanf("%s",arg1);
    printf("How long do you want to monitor? [10, 120] second: ");
    /* need check here */
    scanf("%s",arg2);

    ipc_concat(6,msg,"0",rq->name,id_plus(rq,1),"4",arg1,arg2);

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);

    ipc_disperse(tokens,buffer);

    time_t start, diff;
    time_t ntime;
    char reply[MAXLINE];
    int ret;
    
    start = time(NULL);
    diff = 0;

    if(!strcmp(tokens[1],"0")){
        printf("Monitor rejected: no such flight!\n");
    }
    else{
        printf("Start monitoring...\n");
        ntime = atol(tokens[2]);
        while ( diff < ntime ){
            diff=time(NULL)-start;

            ret = ipc_rx_wait(rq, buffer, 1);
            if(ret>=0){
                /* ipc receive succeeded */
                ipc_disperse(tokens, buffer);
                printf("%s\n",tokens[1]);

                memset(msg, 0, MAXLINE);
                sprintf(reply,"Callback received by %s",rq->name);
                ipc_concat(2,msg,"1",reply);
                ipc_tx(rq, msg);
            }
        }
    }
    
    return 0;
}


static int base_s5(struct requestor* rq){
    char msg[MAXLINE];
    char buffer[MAXLINE];
    char* tokens[MAX_TOKEN];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("wait a second, proceeding...\t");

    ipc_concat(4,msg,"0",rq->name,id_plus(rq,1),"5");

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);

    int num = ipc_disperse(tokens,buffer);

    printf("You have booked %s flight ticket(s) in all:\n",tokens[1]);

    for(int i = 1; i < num/2; i++)
    {
         printf("Flight: %s, Quantity: %s\n", tokens[i*2], tokens[i*2+1]);
    }
    
    
    return 0;
}


static int base_s6(struct requestor* rq){
    char msg[MAXLINE];
    char buffer[MAXLINE];
    char arg1[ARG_LENGTH];
    char arg2[ARG_LENGTH];
    char* tokens[MAX_TOKEN];

    memset(msg, 0, MAXLINE);
    memset(buffer, 0, MAXLINE);

    printf("Flight number you want to cancel: ");
    scanf("%s",arg1);
    printf("Quantity (positive integer): ");
    /* need check here */
    scanf("%s",arg2);

    ipc_concat(6,msg,"0",rq->name,id_plus(rq,1),"6",arg1,arg2);

    ipc_tx(rq, msg);
    ipc_rx(rq, buffer);

    ipc_disperse(tokens,buffer);

    switch (*tokens[1])
    {
        case '1':
            printf("Canceled successfully!\n");
            break;
        case '0':
            printf("You haven't booked that many tickets!\n");
            break;
        case '-':
            printf("No such flight!\n");
            break;
        default:
            printf("ipc error!\n");
            return -1;
    }
    
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

    const struct serv_ops* ops = &base_serv_ops;

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
