# Build deps: pkg-config libevent-devel libbsd-devel
# The patch series must be applied in order before building, e.g. via
# 'make patch'; the default 'all' rule will do this automatically.

# You can override these on the command line, e.g.
# 'make install prefix=/usr mandir=/usr/share/man'
prefix = /usr/local
sbindir = ${prefix}/sbin
mandir = ${prefix}/man

VER = 6.5
#CC = cc
# CFLAGS necessary for building with glibc + libbsd
# (glibc < 2.20: -D_BSD_SOURCE instead of -D_DEFAULT_SOURCE)
CFLAGS = $(shell pkg-config --cflags libbsd-overlay libevent)
CFLAGS += -D_BSD_SOURCE -D_DEFAULT_SOURCE -D_GNU_SOURCE
CFLAGS += -D__dead=''
# these CFLAGS are from OpenBSD src:usr.sbin/slowcgi/Makefile
CFLAGS+= -Wall
CFLAGS+= -Wstrict-prototypes -Wmissing-prototypes
CFLAGS+= -Wmissing-declarations
CFLAGS+= -Wshadow -Wpointer-arith -Wcast-qual
CFLAGS+= -Wsign-compare
# global OpenBSD CFLAGS
CFLAGS += -O2 -pipe
CFLAGS += -Werror-implicit-function-declaration
# debug symbols
CFLAGS += -g

LDFLAGS = $(shell pkg-config --libs libbsd-overlay libevent)

objects := slowcgi.o getdtablecount.o
dist := slowcgi.c slowcgi.8 getdtablecount.c

all: patch slowcgi

slowcgi: $(objects)

$(dist): extract

install: slowcgi
	install -D -m 755 slowcgi $(DESTDIR)${sbindir}/slowcgi
	install -D -m 644 slowcgi.8 $(DESTDIR)${mandir}/man8/slowcgi.8

clean:
	rm -f slowcgi $(objects)

# remove patched sources
distclean: clean
	rm -f $(dist) patch extract

# restore pristine upstream sources
extract:
	for f in $(dist); do cp dist/$$f .; done
	rm -f patch
	echo "Makefile signal - extract done" > extract

# Rather than using Makefile deps for patches, just apply the whole series
# again with 'make distclean patch' if you change or add a patch.
patch: extract
	for f in patches/patch-*; do echo $$f; patch -p0 < $$f; done
	echo "Makefile signal - patch done" > patch

# use stash to include uncommitted changes in the git archive
# This does not include *untracked* files, so if you add a new patch, 'git add'
# it before running 'make tarball'.
tarball:
	my_stash=`git stash create` ;\
	git archive --format=tar.gz --prefix=slowcgi-$(VER)/ -o slowcgi-$(VER).tar.gz $${my_stash:-HEAD}

.SILENT: extract patch
