GLOBALDIR = ./

PROGRAM = $(GLOBALDIR)libHVWrapper.so

CC = gcc

FLAGS = -DUNIX -DLINUX -fPIC -shared

LIBS = -L../bin/x86_64 -lcaenhvwrapper -lncurses -lpthread -ldl -lm

INCLUDEDIR = -I./$(GLOBALDIR) -I./include/

SOURCES = $(GLOBALDIR)HVWrapper.c 

OBJECTS = $(patsubst %.c,%.o,$(SOURCES))

INCLUDES = $(patsubst %.c,%.h,$(SOURCES))

CFLAGS = $(FLAGS)

all: $(PROGRAM)

$(PROGRAM):	$(OBJECTS) 
	$(CC) $(CFLAGS) -o $(PROGRAM) $(OBJECTS) $(LIBS)

$(OBJECTS): $(SOURCES)

$(GLOBALDIR)%.o: $(GLOBALDIR)%.c $(INCLUDES)
	$(CC) $(CFLAGS) $(INCLUDEDIR) -o $@ -c $<

clean:
	rm -f $(OBJECTS) $(PROGRAM)