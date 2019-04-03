#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "def.h"
#include "service.h"
#include "requestor.h"

// Driver code
struct requestor rq1;

struct serv ser = {
    .ops = &base_serv_ops,
};

int main(int argc, char *argv[]) {

    int sn, port;
    sn=0;
    char name[MAX_REQUESTOR_NAME]="test1";
    char serip[IP_LENGTH]="127.0.0.1";
    
    if(argc>2){
        strcpy(name,argv[1]);
        port=atoi(argv[2]);
    }
    else{
        printf("Port you want to use on this machine: ");
        if(scanf("%d",&port)==0) return 1;
        printf("Type in your name: ");
        scanf("%s",name);
    }

    if(argc==4){
        strcpy(serip,argv[3]);
    }

    init_service(&ser);
    init_requestor(&rq1,name,port,"127.0.0.1",serip);

    while(1){
        printf("Welcome %s! Select a service:\n",rq1.name);
        printf("1. Find applicable flights from source to destination.\n");
        printf("2. Get detailed information of a flight: departure time, airfare and vacancies.\n");
        printf("3. Book a flight.\n");
        printf("4. Monitor a flight.\n");
        printf("5. Check order information.\n");
        printf("6. Cancel ordered tickets\n");


getservnum:
        printf("Type in the service you want (number 1-7): ");
        if(scanf("%d",&sn)==0) break;
        if(sn>7 || sn<1) goto getservnum;


        ser.call_service(sn,&rq1);
    }

    free_requestor(&rq1);
    remove_service(&ser);

    return 0;
}
