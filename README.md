# FlightBooking

Xiaohan Fu

Demo: slot 10, 13:15 - 13:30

[TOC]

## Introduction

This is a flight booking system which allows user to search, enquire, book/cancel, monitor flights and review orders. It contains a server app and a client app.

About the two add-on services:

* Cancel flight is a service that allows a user to make seat cancelation on a flight by specifying the
flight identifier and the number of seats to cancel. On successful reservation, an
acknowledgement is returned to the client and the seat availability of the flight
should be updated at the server. In case of incorrect user input (e.g., not-existing
flight identifier or insufficient number of booked seats), a proper error message
should be returned.

* Review orders is a service that allows a user to check/review all the orders/bookings he/she has made. No input is required.

## Get Started

server:
```
python3 server.py [isUDPReliable]
```
When the optional execution argument `isUDPReliable` is specified to be `False`, the server will run in a udp unreliable mode (*at least once semantic*).

python client
```
python3 client.py [server_address] [server_port]
```
c client
```
make
./client.exe [server_address] [server_port]
```
The arguments `server_address` and `server_port` are optional (but they must appear together) and by default set to ('localhost', 2222)

*Note: the python client is more fault tolerent than the c client for wrong inputs (e.g. the user typed in a string when an int is expected). But anyway, we expect the user to interact correctly. The behavior of python and c client may also have some slight difference.*

## Demo Script

You may follow the script to perform tests on the system.

1. Start up the server on an arbitrary computer in the lab
2. Start up three clients on several other computers
3. Work on client 1 and test all services except monitor
    * Test the find flight service
        - Shanghai -> Beijing
        - Shanghai -> Nanjing (no such flight)
    * Test the check flight info service
        - MU110
        - MU123 (no such flight)
    * Test the book flight service
        - MU110 3
        - MU123 3 (no such flight)
        - MU110 20 (not enough vacacies)
    * Test the check order service
    * Test the cancel flight service
        - MU110 1
        - check order
        - MU110 3 (not enough orders)
        - MU123 2 (no such flight)
4. Test the monitor service with client 2 and client 3
    * Client 2 monitor HU222 (no such flight)
    * Client 2 monitor HU201 and client 3 monitor MU110
    * Client 1 book/cancel flights of HU201 and MU110
    * After the monitor interval ends, test arbitrarily any services

## Overall System Design

The flightbooking system is implemented in a **client-server** structure. 

The client app is a combination of a client front-end and server interface. It's responsible for the interaction with users, including reading in the requested service and arguments from the text interface and outputing/displaying the consequent result to users as a front-end as well as the transmission and marshalling of service request to the server as the interface.

The server app is a combination of the server back-end and skeleton. It's responsible for the execution of services, management of database and generation of the result as back-end and also unmarshalling the request received and calling the service functions as a skeleton.

A complete circle (if no fault occurs) is:

* Client reads input from user
* Client marshalls the inputs into bytecode and sends to server by udp
* Server receives the bytecode and unmarshalls it
* Server calls the corresponding function
* Server marshalls the result into bytecode and sends back to client by udp
* Client receives the bytecode and sends an acknowledgement to server
* Client unmarshalls the result and displays the output to user

The callback(monitor) is a little bit different. You may refer to later sections on callback and fault-tolerent measures.

### Database Structure

The database is actually a runtime dictionary stored as a private dictionary inside the server. It's designed to be super intuitive: the Key of the dict is just the idenntifier of the flightNO, the correponding Value is another dict which contains all information relevant. "Details" is a three element array which is repectively the departure time (int), airfare (float) and vacancy (int). The departure hour:minute data can be decoded by dividing the int value with 100 and obtain its quotient and remainder. The airfare and vacancy are straightforward.

The database can be loaded before the server starts from files under same path named as `flights.json` and `booking.json`. If no such files exist, the server will use the internal database per-defined as following:

```python
# flightdb: Dic[flightID] -> details: departuretime, airfare, availibity, src, dest
flightdb = \
    {
        "MU110": {"details": [1800, 1000.3, 10], "src": "Shanghai", "dest": "Beijing", "modified": False},
        "HU201": {"details": [1405, 600.2, 16], "src": "Singapore", "dest": "Bali", "modified": False},
        "MU5125": {"details": [930, 211.1, 52], "src": "Shanghai", "dest": "Beijing", "modified": False}
    }

# bookingdb: Dic[Name][flightID] -> quantity of flightID booked by Name
bookingdb = {"Jordan": {"MU110": 3},
                    "Kobe": {"MU110": 10, "HU201": 3}}
```

On exit, server will save the updated database into `dump_flights.json` and `dump_booking.json`.

### Message Format

The general design logic is: everything is a string. So basically all kinds of data structures are marshalled exactly in the same way as string after they are transformed into a string. 

To marshall a string, considering our system only supports english character message, utf-8 is equivalent to ascii. We decide to directly use the corresponding ascii value a character in its corresponding byte representation. This makes things pretty generic and easy since in all programming languages, ascii or utf-8 encoding of a string or char array can be easily obtained. Besides the correponding bytes, a total length of the byte streams should be included ahead as well. For example, a string "abc" should be marshalled as `b'\x03abc'`. 

But this logic has a limitation that it requires the two ends of the communication have some common knowledge of the order and types of data items of a message. Now let's discuss the common knowledge.

No matter what kind of message it is, it should begin with the messageType information, where 0 - request, 1 - reply, 2 - callback and 3 - acknowledgement. 
* Request represents all the service sent from client to server after it obtains input from user. 
* Reply is sent back by the server on execution of request and contains the desired result or sent back by the client to server on receipt of callback from server.
* Callback is sent by the server, which calls the client on the callback list.
* Acknowledgement is sent by the client to tell the server that it has received the result of request.

The following are the details of each messageType.

#### Request Format

A general request format features the following pattern:
`char(1)string(messageType)char(len(requestorname))string(requestorname)char(len(requestID))string(requestID)char(requestType)string(requestType)...parameters`

* messageType: already explained above
* requesterName: obtained as input when the client start, e.g. Jordan
* requestID: a unique ID for each request (defined by the time in the implementation)
* requestType: out of 6 services from 1-6

e.g. a valid request bytecode sent by client: `b'\x010\x06Jordan\x0213\x014\x05MU110\x0230'`

which maps: messageType = 0, requestorname = Jordan, requestID = 13, requestType = 4, parameters: MU110, 30

#### Reply Format

The server reply byte code format is similar to the one of request except we remove the requesterName, requestID and requestType which can be easily obtained by client itself and we replace the parameters with outputs in same fashion.

e.g. a sample reply bytecode sent from server:
`b'\x011\x011` which maps: messageType= 1, results= 1
 
#### Callback Format

Callback messages' format is pretty simple, just a messageType = 2 followed a string message like "XXX Flight now has x vacancies.".

#### ACK Format

ACK message is similar to request, execept it does not have any arguments. The messageType must be 3 and the requestType be 0. The requestID should be identical to the one of the corresponding request.

### Service I/O Specification
Additionally, The two ends of communication need to know the order and type of arguments and results for each kind of service, which will be discussed in details below.

[] brackets mean this is optional

#### Find Flight

* Arguments: string source, string destination
* Results: int num, [string flightNO1, ...]
    - num: number of matched flights (>=0)
    - flightIDs: an array of strings of flightNOs found (length equal to num)

#### Check Details

* Arguments: string FlightNO
* Results: int res, [int departuretime, float airfare, int vacancy]
  * res: 0 - no such flight; 1 - flight exists, followed by [int departuretime, float airfare, int vacancy]

#### Book Flight

* Arguments: string FlightNO, int quantity (>=1)
* Results: int isSuccessful
  * isSuccessful: 1 - successful; 0 - not enough vacancy; -1 - no such flight

#### Monitor Flight

* Arguments: string FlightNO, int duration (in second, >10 <120)
* Results: int approved, int duration
  * approved: 0 - not approved to monitor; 1 - approved, followed by duration (reconfirmation)

#### Check Orders

* Arguments: None
* Results: int num, [string flightNO, int quantity, ...]
  * num: total number of tickets ordered
  * string flightNO, int quantity: quantity and corresponding flightNo, only exist pairly when num > 0
  
#### Cancel Booking

* Arguments: string FlightNO, int quantity (>=1)
* Results: int isSuccessful
  * isSuccessful: 1 - successful; 0 - not enough booked tickets; -1 - no such flight

### Unmarshalling

Based on the above message bytecode format and service I/O specification as a pre-known common knowledge, the server can umarshall the incoming message into correct requested service with arguments or acknowledgement of a request and the client can unmarshall the incoming message into desired results or display the monitor information on monitor.

## Callback

The funtionality of monitor service is implemented in a callback fasion. The client requests to monitor some service and will start a udp listening interval on approved message received (refer to service I/O specification).

The server will register the client's address and port into a selfly maintained callback list data structure. Each time when another client does some booking or canceling of tickets, the corresponding influenced flights will be marked to be modified in database. After the server has replied the request, it will visit all items stored in the callback list and do two things:

1. first check whether this item is out of interval, if so removed it and visit the next item, else
2. check whether the callback client's target flight is modified, if not, visit the next client otherwise send a callback message to it and wait for its **reply**

Note that in step 2, the server is somehow working like a client and keep trying to send callback message to the client until a reply from it is received. Since the execution of client on receiving a callback message is just printing something on the screen, which is idempotent, we are safely  using the `at least once` semantic here.

## Fault Tolerent Measures for UDP

Basically, we are using the `at most once` semantic for client -> server communication with fault tolerent measures:

1. retransmit request message
2. duplicate filtering
3. retransmit reply

### Retransmit Request Message

A timeout period 1 second is set for the socket. If a transmit ommission occurs at any period of the communication, either a missed request, or a missed reply, the client will retransimit the exactly same request repeated until a reply from server is received. 

### Duplicate Filtering with Adaptive Cutting

Since each request message contains the requester name and the requestID info which are unique for each request, the server maintains a request history list. Each request and its corresponding result marshalled bytecode is added into this list after execution.

Each time when the server receives a request, it will first look up the requester name and requestID pair in the request history to see whether it has already been executed. If not, a normal process will be done otherwise the result bytecode will be directly sent back to the client and jump through all the other steps.

To solve the problem of infinitely growing history list size, we ask the client to send an acknowledgement on receiving the result from server. The server will delete the corresponding request in request history consequently. However, this is an optional requirement. Even if the acknowledgement is missing or the client does not send a ack, everything still works fine. This is designed in terms of flexibility and efficiency. As a result, we don't need any fault tolerence measure to ensure the reliability of acknowledgement transimission.

## Experiment on At-least-once and At-most-once Semantics

We test the difference behavior of at-least-once semantic and at-most-once semantic on same scripts for non-idempotent and idempotent case respectively. We simulate the case that a transmit omission happens such that the request is resent by the client.

Non-idempotent:
```python
blist = []  # request list to be sent sequentially

# test service three
blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('James')) + 'James' + chr(len(str(13))) + str(13) + chr(
    len(str(3))) + str(3) + chr(len("HU201")) + "HU201" + chr(len(str(5))) + str(5), 'utf-8'))

# test service three (duplicated)
blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('James')) + 'James' + chr(len(str(13))) + str(13) + chr(
    len(str(3))) + str(3) + chr(len("HU201")) + "HU201" + chr(len(str(5))) + str(5), 'utf-8'))

# test service six
blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('James')) + 'James' + chr(len(str(15))) + str(15) + chr(
    len(str(6))) + str(6) + chr(len("HU201")) + "HU201" + chr(len(str(3))) + str(3), 'utf-8'))

# test service six (duplicated)
blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('James')) + 'James' + chr(len(str(15))) + str(15) + chr(
    len(str(6))) + str(6) + chr(len("HU201")) + "HU201" + chr(len(str(3))) + str(3), 'utf-8'))
```

Idempotent:
```python
blist = []  # request list to be sent sequentially

# test service two
blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(14))) + str(14) + chr(
        len(str(2))) + str(2) + chr(len("HU201")) + "HU201", 'utf-8'))

# test service two (duplicated)
blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('jordan')) + 'jordan' + chr(len(str(14))) + str(14) + chr(
        len(str(2))) + str(2) + chr(len("HU201")) + "HU201", 'utf-8'))

# test service five
blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('James')) + 'James' + chr(len(str(14))) + str(14) + chr(
    len(str(5))) + str(5), 'utf-8'))

# test service five (duplicated)
blist.append(bytes(chr(len(str(0))) + str(0) + chr(len('James')) + 'James' + chr(len(str(14))) + str(14) + chr(
    len(str(5))) + str(5), 'utf-8'))
```

### At-least-once Semantics

Execution settings of server:
```
/usr/local/bin/python3.7 /Users/reapor.yurnero/PycharmProjects/FlightBooking/server/server.py False
Manually chose udp reliability: False

```
#### Non-Idempotent Script
Monitor log:
```
Welcome monitor! Select a service:
1. Find applicable flights from source to destination.
2. Get detailed information of a flight: departure time, airfare and vacancies.
3. Book a flight.
4. Monitor a flight.
5. Check order information.
6. Cancel ordered tickets
7. Exit
Type in the service you want (number 1-7): 4
Flight number you want to monitor: HU201
How long do you want to monitor? [10, 120] second: 119
Start monitoring...
Flight HU201 now has 11 vacancies!
callback reply sent by client
Flight HU201 now has 6 vacancies!
callback reply sent by client
Flight HU201 now has 9 vacancies!
callback reply sent by client
Flight HU201 now has 12 vacancies!
callback reply sent by client
```

Database final result:
```python
flightdb = \
    {
        "MU110": {"details": [1800, 1000.3, 10], "src": "Shanghai", "dest": "Beijing", "modified": False},
        "HU201": {"details": [1405, 600.2, 12], "src": "Singapore", "dest": "Bali", "modified": False},
        "MU5125": {"details": [930, 211.1, 52], "src": "Shanghai", "dest": "Beijing", "modified": False}
    }
bookingdb = \
    {
        'Jordan': {'MU110': 3},
        'Kobe': {'MU110': 10, 'HU201': 3},
        'James': {'HU201': 4}
    }
```

#### Idempotent Script

Database final result:
```python
flightdb = \
    {
        "MU110": {"details": [1800, 1000.3, 16], "src": "Shanghai", "dest": "Beijing", "modified": False},
        "HU201": {"details": [1405, 600.2, 12], "src": "Singapore", "dest": "Bali", "modified": False},
        "MU5125": {"details": [930, 211.1, 52], "src": "Shanghai", "dest": "Beijing", "modified": False}
    }
bookingdb = \
    {
        'Jordan': {'MU110': 3},
        'Kobe': {'MU110': 10, 'HU201': 3}
    }
```

### At-most-once Semantic
Execution settings of server:
```
/usr/local/bin/python3.7 /Users/reapor.yurnero/PycharmProjects/FlightBooking/server/server.py

```

#### Non-idempotent script

Monitor Log:
```
Start monitoring...
Flight HU201 now has 11 vacancies!
callback reply sent by client
Flight HU201 now has 14 vacancies!
callback reply sent by client
```

Final db result:
```python
flightdb = \
    {
        "MU110": {"details": [1800, 1000.3, 10], "src": "Shanghai", "dest": "Beijing", "modified": False},
        "HU201": {"details": [1405, 600.2, 14], "src": "Singapore", "dest": "Bali", "modified": False},
        "MU5125": {"details": [930, 211.1, 52], "src": "Shanghai", "dest": "Beijing", "modified": False}
    }
bookingdb = \
    {
        'Jordan': {'MU110': 3},
        'Kobe': {'MU110': 10, 'HU201': 3},
        'James': {'HU201': 2}
    }
```

#### Idempotent script

Final db result:
```python
flightdb = \
    {
        "MU110": {"details": [1800, 1000.3, 16], "src": "Shanghai", "dest": "Beijing", "modified": False},
        "HU201": {"details": [1405, 600.2, 12], "src": "Singapore", "dest": "Bali", "modified": False},
        "MU5125": {"details": [930, 211.1, 52], "src": "Shanghai", "dest": "Beijing", "modified": False}
    }
bookingdb = \
    {
        'Jordan': {'MU110': 3},
        'Kobe': {'MU110': 10, 'HU201': 3}
    }
```

### Experiment Conclusions

The at-most-once semantics works properly for both non-idempotent and idempotent operations on duplicated request,
 while at-least-once only works properly for idempotent operations and will lead to wrong answer on non-idempotent case.


## Potential Updates in Future

* Login system which binds username with a password (may implement some interesting crypoto algos)
* A standalone remote database server with mongodb or sql which can be updated real-timely
* A GUI (may practice with qt gui design)


