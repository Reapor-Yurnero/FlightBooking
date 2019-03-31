#ifndef __IPC_H
#define __IPC_H

extern int ipc_tx(struct requestor* rq, const char* msg);
extern int ipc_rx(struct requestor* rq, char* recv);
extern char* ipc_cat(char* dest, const char* src);
extern int ipc_concat(int num, char* dest, ...);

#endif /* __IPC_H */