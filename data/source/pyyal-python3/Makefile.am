# Note that we cannot use: AUTOMAKE_OPTIONS = subdir-objects
# subdir-objects will compile the source files to a single version of Python.
# Since subdir-objects is being deprecated we copy the source files instead.
am__installdirs = "$$(DESTDIR)$$(pyexecdir3)"
pyexecdir = $$(pyexecdir3)

if HAVE_PYTHON3
AM_CFLAGS = \
	-I$$(top_srcdir)/include \
	-I$$(top_srcdir)/common \
	@LIBCERROR_CPPFLAGS@ \
	@LIBCDATA_CPPFLAGS@ \
	@LIBCLOCALE_CPPFLAGS@ \
	@LIBCSPLIT_CPPFLAGS@ \
	@LIBUNA_CPPFLAGS@ \
	@LIBCFILE_CPPFLAGS@ \
	@LIBCPATH_CPPFLAGS@ \
	@LIBBFIO_CPPFLAGS@ \
	@LIBFGUID_CPPFLAGS@

am_${python_module_name}_la_rpath = -rpath $$(pyexecdir3)

BUILT_SOURCES = \
	${python_module_name}.c ${python_module_name}.h \
	${python_module_name}_error.c ${python_module_name}_error.h \
	${python_module_name}_file_object_io_handle.c ${python_module_name}_file_object_io_handle.h \
	${python_module_name}_libbfio.h \
	${python_module_name}_libcerror.h \
	${python_module_name}_libclocale.h \
	${python_module_name}_${library_name}.h \
	${python_module_name}_python.h \
	${python_module_name}_unused.h

pyexec_LTLIBRARIES = ${python_module_name}.la

nodist_${python_module_name}_la_SOURCES = $$(BUILT_SOURCES)

${python_module_name}_la_LIBADD = \
	@LIBCERROR_LIBADD@ \
	../${library_name}/${library_name}.la \
	@LIBCDATA_LIBADD@ \
	@LIBCLOCALE_LIBADD@ \
	@LIBCSPLIT_LIBADD@ \
	@LIBUNA_LIBADD@ \
	@LIBCFILE_LIBADD@ \
	@LIBCPATH_LIBADD@ \
	@LIBBFIO_LIBADD@ \
	@LIBFGUID_LIBADD@

${python_module_name}_la_CPPFLAGS = $$(PYTHON3_CPPFLAGS)
${python_module_name}_la_LDFLAGS  = -module -avoid-version $$(PYTHON3_LDFLAGS)

$$(BUILT_SOURCES):
	/bin/cp -f $$(top_srcdir)/${python_module_name}/$$@ $$@

endif

MAINTAINERCLEANFILES = \
	Makefile.in

clean-local:
	/bin/rm -f ${python_module_name}*.[ch]

distclean: clean
	/bin/rm -f Makefile

