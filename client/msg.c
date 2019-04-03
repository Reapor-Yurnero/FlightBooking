#include <stdlib.h>
#include <string.h>
#include "msg.h"
#include "def.h"

int clean_msg(struct message* m){
    memset(m->send, 0, MAXLINE);
    memset(m->recv, 0, MAXLINE);
    memset(m->tokens, 0 ,MAX_TOKEN);
    return 0;
}

int init_msg(struct message* m){

    m->send = malloc(sizeof(char)*MAXLINE);
    m->recv = malloc(sizeof(char)*MAXLINE);
    m->tokens = malloc(sizeof(char *)*MAX_TOKEN);
    clean_msg(m);
    return 0;
}

int free_msg(struct message* m){
    free(m->send);
    free(m->recv);
    free(m->tokens);
    return 0;
}
