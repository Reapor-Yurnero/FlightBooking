#ifndef __IPC_H
#define __IPC_H

#define IPC_TIMEOUT 2 /* 2 second */

extern int ipc_tx(struct requestor* rq, const char* msg);
extern int ipc_rx(struct requestor* rq, char* recv);
extern int ipc_rx_wait(struct requestor* rq, char* recv, int timeout);
extern char* ipc_cat(char* dest, const char* src);
extern int ipc_concat(int num, char* dest, ...);
extern int ipc_disperse(char** tokens,char* buffer);

#endif /* __IPC_H */