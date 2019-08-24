#  Copyright (C) 2007 Jacek Śliwerski (rzyjontko)
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.  

include ../config.mak

DEPDIR = .deps

DEFINES += -D_GNU_SOURCE=1
CFLAGS += -Wall -fpic
INCLUDES = 
COMPILE = LANG=C gcc $(CFLAGS) $(DEFINES)
LDFLAGS = -lsqlite3

TRANOBJS = xmalloc.o hash.o phrase.o storage.o
OBJS = xmalloc.o hash.o phrase.o opentran.o

all: libopentran.so tran

libopentran.so: $(OBJS)
	@echo "LD	$@"
	$(Q)gcc -shared $(LDFLAGS) -o $@ $^

tran: $(TRANOBJS) main.o
	@echo "LD	$@"
	$(Q)gcc $(LDFLAGS) -o $@ $^

_tran.so: $(TRANOBJS) tran.o
	@echo "LD	$@"
	$(Q)gcc -shared $(LDFLAGS) -o $@ $^

tran.c: tran.i
	@echo "SWIG	$@"
	$(Q)swig -python -o $@ $^

.c.o:
	@echo "CC	$@"
	$(Q)if $(COMPILE) -MT $@ -MP -MF "$(DEPDIR)/$*.Tpo" -MD \
	  -c -o $@ $<; then mv -f "$(DEPDIR)/$*.Tpo" "$(DEPDIR)/$*.po"; \
        else rm -f "$(DEPDIR)/$*.Tpo"; exit 1; fi

clean:
	rm -f *.so *.o tran.c tran.py *.pyc

include $(DEPDIR)/hash.po
include $(DEPDIR)/main.po
include $(DEPDIR)/xmalloc.po
include $(DEPDIR)/phrase.po
include $(DEPDIR)/storage.po
include $(DEPDIR)/tran.po
include $(DEPDIR)/opentran.po
