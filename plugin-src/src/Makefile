#!/usr/bin/make -f
# New Movie Library player plugin (VST3 + CLAP). Build from the plugin/ folder with `make`.
NAME = NewMovieLibrary

FILES_DSP = \
	PluginDSP.cpp \
	engine/Catalog.cpp \
	engine/Engine.cpp \
	engine/Samples.cpp \
	generated/catalog_data.cpp

FILES_UI = \
	PluginUI.cpp \
	../dpf-widgets/opengl/DearImGui.cpp

include ../dpf/Makefile.plugins.mk

# keep NaN/Inf checks working under -ffast-math (the engine's safety net relies on them)
BUILD_CXX_FLAGS += -std=gnu++17 -fno-finite-math-only -I../dpf-widgets/opengl -I../third_party -I.

all: vst3 clap
