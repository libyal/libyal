include_HEADERS = \
	${library_name}.h

pkginclude_HEADERS = \
${pkginclude_headers}

EXTRA_DIST = \
	${library_name}.h.in \
	${library_name}/definitions.h.in \
	${library_name}/features.h.in \
	${library_name}/types.h.in

MAINTAINERCLEANFILES = \
	Makefile.in

distclean: clean
	-rm -f ${library_name}.h
	-rm -f ${library_name}/definitions.h
	-rm -f ${library_name}/features.h
	-rm -f ${library_name}/types.h
	-rm -f Makefile

