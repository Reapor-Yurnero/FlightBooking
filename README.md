# FlightBooking

Author: Xiaohan Fu

Demo: slot 10, 13:15 - 13:30

## Introduction & Get Started

This is a flight booking system which allows user to search, enquire, book/cancel, monitor flights and review orders. It contains a server app and a client app.

For server part:
```
python3 server.py [isUDPReliable]
```
When the optional execution argument isUDPReliable specifying as `False`, the server will run in a udp unreliable mode (*at least once semantic*).
 
For client part:
```
python3 client.py [server address] [server port]
```
The arguments `server address` and `server port` are optional and by default set to ('localhost',2222)

## Demo Script

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

## Overall Structure Design

The flightbooking system is implemented in a **client-server** structure. 

The client app is responsible for the interaction with users, including reading in the requested service and arguments from the text interface and outputing/displaying the consequent result to users.

The server is responsible for the execution of services, management of database and generation of the result.

Our whole system is illustrated in the following graph (TODO).

In the following subsections, I will develop
### Database Structure

The database is actually a runtime dictionary stored as a private dictionary inside the server. It's designed to be super intuitive: the Key of the dict is just the idenntifier of the flightNO, the correponding Value is another dict which contains all information relevant. "Details" is a three element array which is repectively the departure time (int), airfare (float) and vacancy (int). The departure hour:minute data can be decoded by dividing the int value with 100 and obtain its quotient and remainder. The airfare and vacancy are straightforward.

Example:

## Marshalling

client request byte code format:

char(1)string(messageType)char(len(requestorname))string(requestorname)char(len(requestID))string(requestID)char(requestType)string(requestType)...parameters

* messageType -> 0 | 1 | 2 (request|reply|callback, only request for client)
* requesterName obtained as input when the client start, e.g. Jordan
* requestID: incremented for each distinct request, (not incremented for resend of request the client hasn't recieved the reply from server within TIMEOUT)
* requestType: out of 6 services from 1-6

e.g. a valid bytecode sent by client: b'\x010\x06Jordan\x0213\x014\x05MU110\x0230'

which maps: messageType = 0, requestorname = Jordan, requestID = 13, requestType = 4, parameters: MU110, 30

the server reply byte code format is similar except we remove the requesterName, requestID and requestType which can be easily accessed by client itself and we replace the parameters with outputs in same fashion.

## Callback

The client should start the udp listening while loop for duration seconds time when it receives the reply as approved(true or 1) for the service 4.

## Service I/O Specification (TODO)

## Experiment on At-least-one Semantics and At-most-one Semantics

We test the difference behavior of at-least-one semantics and at-most-once semantics on same scripts of non-idempotent and idempotent.

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

### At-least-one Semantics

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

#### Idenpotent script

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




