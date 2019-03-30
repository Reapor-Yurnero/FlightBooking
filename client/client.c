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

    init_service(&ser);
    init_requestor(&rq1,"test1",8088,"localhost");

    // printf("",ser.ops);
    ser.ops->s1(ser.sockfd, ser.servaddr);

    free_requestor(&rq1);
    remove_service(&ser);

    return 0;
}
