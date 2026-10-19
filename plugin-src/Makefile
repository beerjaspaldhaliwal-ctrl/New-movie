#!/usr/bin/make -f
# New Movie Library player plugin
#   make                      -> native build (Linux)
#   make WINDOWS=true CC=x86_64-w64-mingw32-gcc CXX=x86_64-w64-mingw32-g++   -> Windows build
include dpf/Makefile.base.mk

all: dgl plugin

dgl:
	$(MAKE) -C dpf/dgl opengl

plugin: dgl
	$(MAKE) all -C src

clean:
	$(MAKE) clean -C dpf/dgl
	$(MAKE) clean -C src
	rm -rf bin build

.PHONY: dgl plugin
