CC = gcc
CFLAGS = -shared -O2 -fPIC -Wall -Wextra

ifeq ($(OS),Windows_NT)
	TARGET = libstorageops.dll
else
	UNAME := $(shell uname)
	ifeq ($(UNAME),Darwin)
		TARGET = libstorageops.dylib
	else
		TARGET = libstorageops.so
	endif
endif

SOURCES = crc32_fast.c block_ops.c

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) -o $@ $(SOURCES)

clean:
	rm -f $(TARGET) *.o

.PHONY: all clean
