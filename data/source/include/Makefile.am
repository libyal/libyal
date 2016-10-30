include_HEADERS = \
	${library_name}.h

pkginclude_HEADERS = \
	${library_name}/codepage.h \
	${library_name}/definitions.h \
	${library_name}/error.h \
	${library_name}/extern.h \
	${library_name}/features.h \
	${library_name}/types.h

EXTRA_DIST = \
	${library_name}.h.in \
	${library_name}/definitions.h.in \
	${library_name}/features.h.in \
	${library_name}/types.h.in

MAINTAINERCLEANFILES = \
	Makefile.in

distclean: clean
	/bin/rm -f ${library_name}.h
	/bin/rm -f ${library_name}/definitions.h
	/bin/rm -f ${library_name}/features.h
	/bin/rm -f ${library_name}/types.h
	/bin/rm -f Makefile

