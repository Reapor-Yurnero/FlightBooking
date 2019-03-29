#include "service.h"

static int base_s1(){
    return 0;
}

const struct serv_ops base_serv_ops = {
    .s1 = base_s1,
}
