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
