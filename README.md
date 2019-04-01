# FlightBooking

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

### Conclusions

The at-most-once semantics works properly for both non-idempotent and idempotent operations on duplicated request,
 while at-least-once only works properly for idempotent operations and will lead to wrong answer on non-idempotent case.




