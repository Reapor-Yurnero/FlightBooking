#ifndef __MSG_H
#define __MSG_H

struct message
{
    char* send;
    char* recv;
    char** tokens;
};

extern int clean_msg(struct message* m);
extern int init_msg(struct message* m);
extern int free_msg(struct message* m);

#endif /* __MSG_H */