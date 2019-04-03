#ifndef __SERVICE_H
#define __SERVICE_H

#include "def.h"
#include "requestor.h"
#include "msg.h"

#define SER_FIND        1
#define SER_GETDETAIL   2
#define SER_BOOK        3
#define SER_MONITOR     4
#define SER_ORDERINFO   5
#define SER_CANCEL      6
#define SER_EXIT        7

struct serv_ops {

    /*  A service that allows a user to query the flight identifier(s) by specifying the source
        and destination places. If multiple flights match the source and destination places,
        all of them should be returned to the user. If no flight matches the source and
        destination places, an error message should be returned.
    */
    int (*s1)(struct requestor* rq, struct message* m);

    /*  A service that allows a user to query the departure time, airfare and seat
        availability by specifying the flight identifier. If the flight with the requested identifier
        does not exist, an error message should be returned.
    */
    int (*s2)(struct requestor* rq, struct message* m);

    /*  A service that allows a user to make seat reservation on a flight by specifying the
    flight identifier and the number of seats to reserve. On successful reservation, an
    acknowledgement is returned to the client and the seat availability of the flight
    should be updated at the server. In case of incorrect user input (e.g., not-existing
    flight identifier or insufficient number of available seats), a proper error message
    should be returned.
    */
    int (*s3)(struct requestor* rq, struct message* m);

    /*  A service that allows a user to monitor updates made to the seat availability
    information of a flight at the server through callback for a designated time period
    called monitor interval. To register, the client provides the flight identifier and the
    length of monitor interval to the server. After registration, the Internet address and
    the port number of the client are recorded by the server. During the monitor
    interval, every time a seat reservation is made by any client on the flight, the
    updated seat availability of the flight is sent by the server to the registered client(s)
    through callback. After the expiration of the monitor interval, the client record is
    removed from the server which will no longer deliver the updates of the flight to
    the client. For simplicity, you may assume that the user that has issued a register
    request for monitoring is blocked from inputting any new request until the monitor
    interval expires, i.e., the client simply waits for the updates from the server during
    the monitor interval. As a result, you do not have to use multiple threads at a
    client. However, your implementation should allow multiple clients to monitor
    updates to the flights concurrently.
    */
    int (*s4)(struct requestor* rq, struct message* m);

    /*  In addition to the above services, you are required design and implement two
    more operations on the flights through client-server communication. One of
    them should be idempotent and the other should be non-idempotent. Describe
    your design in the report.
    */
    int (*s5)(struct requestor* rq, struct message* m);
    int (*s6)(struct requestor* rq, struct message* m);

};

struct serv {

    int (*call_service)(int sn, struct requestor* rq);
    /* we may handle concurrency in service system, keep this structure */
    const struct serv_ops* ops;

};

extern int init_service(struct serv* s);
extern int remove_service(struct serv* s);

extern const struct serv_ops base_serv_ops;

#endif /* __SERVICE_H */
