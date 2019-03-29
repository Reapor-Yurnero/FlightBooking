IDIR =../include
CC=gcc
CFLAGS=-I$(IDIR)

ODIR =.
LDIR =../lib
BDIR =.

LIBS=-lm

_DEPS = 
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_OBJ = client.o 
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

_EXE = client.exe
EXE = $(BDIR)/$(_EXE)

$(ODIR)/%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

$(EXE): $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ 