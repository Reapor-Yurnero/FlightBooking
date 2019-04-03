#include <stdio.h>
#include "def.h"
#include "service.h"
#include "requestor.h"

// Driver code
struct requestor rq1;

struct serv ser = {
    .ops = &base_serv_ops,
};

int main() {

    int sn=1;
    int port = 3333;
    char name[MAX_REQUESTOR_NAME] = "test1";
    
    printf("Port you want to use on this machine: ");
    scanf("%d",&port);
    printf("Type in your name: ");
    scanf("%s",name);

    init_service(&ser);
    init_requestor(&rq1,name,port,"127.0.0.1");

    while(1){
        printf("Welcome %s! Select a service:\n",rq1.name);
        printf("1. Find applicable flights from source to destination.\n");
        printf("2. Get detailed information of a flight: departure time, airfare and vacancies.\n");
        printf("3. Book a flight.\n");
        printf("4. Monitor a flight.\n");
        printf("5. Check order information.\n");
        printf("6. Cancel ordered tickets\n");
        printf("Type in the service you want (number 1-7): ");
        scanf("%d", &sn);
        ser.call_service(sn,&rq1);
    }

    free_requestor(&rq1);
    remove_service(&ser);

    return 0;
}
