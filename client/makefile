IDIR =../include
CC=gcc
CFLAGS=-I$(IDIR) -std=c99 -g

ODIR =.
LDIR =../lib
BDIR =.

LIBS=-lm

_DEPS = def.h requestor.h service.h ipc.h msg.h
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_OBJ = requestor.o base_service.o client.o ipc.o msg.o
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

_EXE = client.exe
EXE = $(BDIR)/$(_EXE)

$(ODIR)/%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

$(EXE): $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(_EXE)
