#!/usr/bin/env bash
# Script to generate the Borland's C++ Compiler 5.5 Makefiles

EXIT_SUCCESS=0;
EXIT_FAILURE=1;

REQUIRES_ZLIB=0;

if test ! -f configure.ac;
then
	echo "Missing: configure.ac";

	exit ${EXIT_FAILURE};
fi

PROJECT=`grep -A 1 'AC_INIT' configure.ac | grep -v 'AC_INIT' | sed 's/^[^\[]*\[//;s/\][^\]]*$//'`;
PREFIX=`echo ${PROJECT} | sed 's/lib//'`;

# Do not compile .Net or Python bindings.
for DIRECTORY in lib* *tools tests;
do
	if test ! -d ${DIRECTORY};
	then
		continue;
	fi
	if test ! -f ${DIRECTORY}/Makefile.am;
	then
		continue;
	fi

	# Determine the build targets.
	grep -e '^bin_PROGRAMS' ${DIRECTORY}/Makefile.am > /dev/null;
	BIN_PROGRAMS=$?;

	grep -e '^check_PROGRAMS' ${DIRECTORY}/Makefile.am > /dev/null;
	CHECK_PROGRAMS=$?;

	if test ${BIN_PROGRAMS} -eq 0;
	then
		BUILD_TARGETS=`sed '/^AM_CPPFLAGS =/,/^bin_PROGRAMS =/ { d }; /^$/,$ { d }' ${DIRECTORY}/Makefile.am | sed 's/^\s*//;s/[ ]*\\\\//' | tr '\n' ' '`;

	elif test ${CHECK_PROGRAMS} -eq 0;
	then
		BUILD_TARGETS=`sed '/^AM_CPPFLAGS =/,/^check_PROGRAMS =/ { d }; /^$/,$ { d }' ${DIRECTORY}/Makefile.am | sed 's/^\s*//;s/[ ]*\\\\//' | tr '\n' ' '`;

	else
		BUILD_TARGETS="${DIRECTORY}";
	fi

	AM_CPPFLAGS=`sed '/^AM_LFLAGS =/,/^$/ { d }; /^if / { d }; /^AM_CPPFLAGS =/ { d }; /^$/,$ { d }' ${DIRECTORY}/Makefile.am | sed 's/^\s*//;s/[ ]*\\\\//' | tr '\n' ' '`;

	# Determine the include directories.
	INCLUDES=`echo ${AM_CPPFLAGS} | tr ' ' '\n' | grep -e '^@LIB[^_]*_CPPFLAGS@$' | grep -v -e '^@LIBCRYPTO_CPPFLAGS@$' -e '^@LIBFUSE_CPPFLAGS@$' | sed 's/^@\([^_]*\)_CPPFLAGS@$/..\\\\\1/' | tr '[A-Z]' '[a-z]' | tr '\n' ';'`;

	# Determine the definitions.
	DEFINITIONS_PART1=`echo ${AM_CPPFLAGS} | tr ' ' '\n' | grep -e '@LIB[^_]*_CPPFLAGS@' | sed 's/^@\([^_]*\)_CPPFLAGS@$/-DHAVE_LOCAL_\1/' | tr '\n' ' '`;

	if test ${DIRECTORY} = ${PROJECT};
	then
		DEFINITIONS_PART2=`echo -D${DIRECTORY}_DLL_EXPORT | tr '[a-z]' '[A-Z]'`;

	elif test ${DIRECTORY} = "${PREFIX}tools" || test ${DIRECTORY} = "tests";
	then
		DEFINITIONS_PART2=`echo -D${DIRECTORY}_DLL_IMPORT | tr '[a-z]' '[A-Z]'`;

	else
		DEFINITIONS_PART2=`echo -DHAVE_LOCAL_${DIRECTORY} | tr '[a-z]' '[A-Z]'`;
	fi
	DEFINITIONS="${DEFINITIONS_PART1}${DEFINITIONS_PART2}";

	grep '@ZLIB_CPPFLAGS@' ${DIRECTORY}/Makefile.am > /dev/null;
	if test $? -eq 0;
	then
		INCLUDES="${INCLUDES}..\\..\\zlib;";
		DEFINITIONS="${DEFINITIONS} -DZLIB_DLL";
	fi
	# Note that since Borland's C++ Compiler 5.5 defines memory.h and thus
	# ..\common must be included before $(BCCDIR)\Include

	# Note that for Borland's C++ Compiler 5.5 make the default is the first build target
        # not target all. Hence we must have all as the first bulid target to have the correct behavior.

	FILENAME="${DIRECTORY}/Makefile.bcc";

	echo "Creating: ${FILENAME}";

	cat > ${FILENAME} <<EOT
# Borland's C++ Compiler 5.5 Makefile

CC       = bcc32
ILINK32  = ilink32
IMPLIB   = implib
TLIB     = tlib
RM       = del
BCCDIR   = C:\\Borland\\BCC55

CFLAGS   = -5 -O2 -tW -w-aus -w-ccc -w-csu -w-par -w-pia -w-rch -w-inl -w-ngu -w-pro
LDFLAGS  = -V4.0 -c -x -Gn
DEFS     = -DNDEBUG -DWIN32 -DWINVER=0x0501 -DUNICODE ${DEFINITIONS}
INCLUDES = -I..\\include;..\\common;${INCLUDES}.;\$(BCCDIR)\\Include;

.SUFFIXES: .c

.c.obj:
	\$(CC) -c \$(INCLUDES) \$(CFLAGS) \$(DEFS) \$<

all:	${BUILD_TARGETS}

clean:
	\$(RM) *.exe *.dll *.lib *.obj
EOT

	for BUILD_TARGET in ${BUILD_TARGETS};
	do
		# Determine the source files.
		if test ${DIRECTORY} = "${PREFIX}tools" || test ${DIRECTORY} = "tests";
		then
			SOURCES=`sed "/^AM_CPPFLAGS =/,/^${BUILD_TARGET}_SOURCES =/ { d }; /^$/,$ { d }" ${DIRECTORY}/Makefile.am | sed 's/^\s*//;s/[ ]*\\\\//' | tr '\n' ' '`;
		else
			SOURCES=`sed "/^AM_LFLAGS =/,/^$/ { d }; /^if / { d }; /^AM_CPPFLAGS =/,/^${BUILD_TARGET}_la_SOURCES =/ { d }; /^endif$/ { d }; /^$/,$ { d }" ${DIRECTORY}/Makefile.am | sed 's/^\s*//;s/[ ]*\\\\//' | tr '\n' ' '`;
		fi

		# Assume that the .c and .h files for .l and .y have been generated.
		SOURCE_FILES=`echo ${SOURCES} | tr ' ' '\n' | sed 's/\.[ly]$/.c/' | grep -e '\.c$' | tr '\n' ' '`;

		# Determine the object files for tlib and prefix them with a "+".
		TLIB_OBJECTS=`echo ${SOURCE_FILES} | tr ' ' '\n'| sed 's/^/+/;s/\.c$/.obj/' | tr '\n' ' '`;

		# Determine the library dependencies. 
		if test ${DIRECTORY} = "${PREFIX}tools" || test ${DIRECTORY} = "tests";
		then
			LIBADD=`sed "/^AM_CPPFLAGS =/,/^${BUILD_TARGET}_LDADD =/ { d }; /^$/,$ { d }" ${DIRECTORY}/Makefile.am | sed 's/^\s*//;s/[ ]*\\\\//' | tr '\n' ' '`;

			LIBRARIES=`echo ${LIBADD} | tr ' ' '\n' | grep -e '^@LIB[^_]*_LIBADD@$' | grep -v -e '^@LIBCRYPTO_LIBADD@$' -e '^@LIBDL_LIBADD@$' -e '^@LIBFUSE_LIBADD@$' -e '^@LIBUUID_LIBADD@$' | sed 's/^@\([^_]*\)_LIBADD@$/\1/' | tr '[A-Z]' '[a-z]' | tr '\n' ' '`;

			# Determine the dependencies of the dependencies.
			LIBADD="";
			for LIBRARY in ${LIBRARIES};
			do
				SUB_LIBADD=`sed "/^AM_LFLAGS =/,/^$/ { d }; /^if / { d }; /^AM_CPPFLAGS =/,/^${LIBRARY}_la_LIBADD =/ { d }; /^endif$/ { d }; /^$/,$ { d }" ${LIBRARY}/Makefile.am | sed 's/^\s*//;s/[ ]*\\\\//' | tr '\n' ' '`;
				if test ! -z "${SUB_LIBADD}";
				then
					SUB_LIBRARIES=`echo ${SUB_LIBADD} | tr ' ' '\n' | grep -e '^@LIB[^_]*_LIBADD@$' | grep -v -e '^@LIBCRYPTO_LIBADD@$' -e '^@LIBDL_LIBADD@$' -e '^@LIBFUSE_LIBADD@$' -e '^@LIBUUID_LIBADD@$' | sed 's/^@\([^_]*\)_LIBADD@$/..\\\\\1\\\\\1.lib/' | tr '[A-Z]' '[a-z]' | tr '\n' ' '`;

					LIBADD="${LIBADD} ${SUB_LIBRARIES}";
				fi
				LIBADD="${LIBADD} ..\\${LIBRARY}\\${LIBRARY}.lib";
			done
			LIBRARIES=`echo ${LIBADD} | tr ' ' '\n' | sort | uniq | tr '\n' ' '`;
		else
			LIBADD=`sed "/^AM_LFLAGS =/,/^$/ { d }; /^if / { d }; /^AM_CPPFLAGS =/,/^${BUILD_TARGET}_la_LIBADD =/ { d }; /^endif$/ { d }; /^$/,$ { d }" ${DIRECTORY}/Makefile.am | sed 's/^\s*//;s/[ ]*\\\\//' | tr '\n' ' '`;
			LIBRARIES=`echo ${LIBADD} | tr ' ' '\n' | grep -e '^@LIB[^_]*_LIBADD@$' | grep -v -e '^@LIBCRYPTO_LIBADD@$' -e '^@LIBDL_LIBADD@$' -e '^@LIBFUSE_LIBADD@$' -e '^@LIBUUID_LIBADD@$' | sed 's/^@\([^_]*\)_LIBADD@$/..\\\\\1\\\\\1.lib/' | tr '[A-Z]' '[a-z]' | tr '\n' ' '`;

		fi

		if test ${DIRECTORY} = "${PREFIX}tools" || test ${DIRECTORY} = "tests";
		then
			LIBRARIES="${LIBRARIES}..\\${PROJECT}\\${PROJECT}.lib ";
		fi

		# TODO: add support for uuid.lib?
		# echo ${LIBADD} | tr ' ' '\n' | grep '@LIBUUID_LIBADD@' > /dev/null;
		# if test $? -eq 0;
		# then
		#	LIBRARIES="${LIBRARIES}\$(BCCDIR)\\Lib\\uuid.lib ";
		# fi

		echo ${LIBADD} | tr ' ' '\n' | grep '@ZLIB_LIBADD@' > /dev/null;
		if test $? -eq 0;
		then
			LIBRARIES="${LIBRARIES}..\\..\\zlib\\zlib.lib ";
			REQUIRES_ZLIB=1;
		fi

		cat >> ${FILENAME} <<EOT

${BUILD_TARGET}_SOURCES = ${SOURCE_FILES}

${BUILD_TARGET}_OBJECTS = \$(${BUILD_TARGET}_SOURCES:.c=.obj)

${BUILD_TARGET}_LIBADD  = ${LIBRARIES}

${BUILD_TARGET}: \$(${BUILD_TARGET}_LIBADD) \$(${BUILD_TARGET}_OBJECTS)
EOT

		if test ${BUILD_TARGET} = ${PROJECT};
		then
			cat >> ${FILENAME} <<EOT
	\$(RM) ${BUILD_TARGET}.dll ${BUILD_TARGET}.lib
	\$(ILINK32) -Tpd -j\$(BCCDIR)\\Lib -L\$(BCCDIR)\\Lib \$(LDFLAGS) \$(${BUILD_TARGET}_OBJECTS) c0d32w.obj, ${BUILD_TARGET}.dll, , \$(${BUILD_TARGET}_LIBADD) import32.lib cw32.lib, ,
	\$(IMPLIB) ${BUILD_TARGET}.lib ${BUILD_TARGET}.dll
EOT

		elif test ${DIRECTORY} = "${PREFIX}tools" || test ${DIRECTORY} = "tests";
		then
			cat >> ${FILENAME} <<EOT
	\$(RM) ${BUILD_TARGET}.exe
	\$(ILINK32) -Tpe -j\$(BCCDIR)\\Lib -L\$(BCCDIR)\\Lib -ap \$(LDFLAGS) \$(${BUILD_TARGET}_OBJECTS) c0x32w.obj, ${BUILD_TARGET}.exe, , \$(${BUILD_TARGET}_LIBADD) import32.lib cw32.lib, ,
EOT

		else
			cat >> ${FILENAME} <<EOT
	\$(RM) ${BUILD_TARGET}.lib
	\$(TLIB) ${BUILD_TARGET}.lib ${TLIB_OBJECTS}
EOT
		fi
	done
done

DIRECTORY=`basename $PWD`;

if test ${REQUIRES_ZLIB} -ne 0;
then
	if test ! -d ../zlib;
	then
		echo "WARNING: missing directory: ../zlib";

		FILENAME="../zlib_Makefile.bcc";
	else
		FILENAME="../zlib/Makefile.bcc";
	fi

	echo "Creating: ${FILENAME}";

	cat > ${FILENAME} <<EOT
# Borland's C++ Compiler 5.5 Makefile

CC       = bcc32
ILINK32  = ilink32
IMPLIB   = implib
TLIB     = tlib
RM       = del
BCCDIR   = C:\\Borland\\BCC55

CFLAGS   = -5 -O2 -tW -w-aus -w-ccc -w-csu -w-par -w-pia -w-rch -w-inl -w-ngu -w-pro
LDFLAGS  = -V4.0 -c -x -Gn
DEFS     = -DNDEBUG -DWIN32 -DUNICODE -DZLIB_DLL
INCLUDES = -I.;\$(BCCDIR)\\Include;

LIBADD   = 

.SUFFIXES: .c

.c.obj:
	\$(CC) -c \$(INCLUDES) \$(CFLAGS) \$(DEFS) \$<

all:	zlib

clean:
	\$(RM) *.dll *.lib *.obj

zlib_SOURCES = adler32.c compress.c crc32.c deflate.c gzclose.c gzlib.c gzread.c gzwrite.c infback.c inffast.c inflate.c inftrees.c trees.c uncompr.c zutil.c

zlib_OBJECTS = \$(zlib_SOURCES:.c=.obj)

zlib: \$(zlib_OBJECTS)
	\$(RM) zlib.dll zlib.lib
	\$(ILINK32) -Tpd -j\$(BCCDIR)\\Lib -L\$(BCCDIR)\\Lib \$(LDFLAGS) \$(zlib_OBJECTS) c0d32w.obj, zlib.dll, , import32.lib cw32.lib, ,
	\$(IMPLIB) zlib.lib zlib.dll
EOT

fi

# Create make.bat and make_clean.bat to recurse the sub directories.
echo "Creating: make.bat";

cat > make.bat <<EOT
@echo off
set PATH=%PATH%;C:\\Borland\\BCC55\\bin

EOT

echo "Creating: make_clean.bat";

cat > make_clean.bat <<EOT
@echo off
set PATH=%PATH%;C:\\Borland\\BCC55\\bin

EOT

if test ${REQUIRES_ZLIB} -ne 0;
then
	cat >> make.bat <<EOT
cd ..\\zlib
make.exe -fMakefile.bcc
cd ..\\${DIRECTORY}

EOT
	cat >> make_clean.bat <<EOT
cd ..\\zlib
make.exe -fMakefile.bcc
cd ..\\${DIRECTORY}

EOT

fi

SUBDIRS=`sed '/^ACLOCAL_AMFLAGS =/,/^SUBDIRS =/ { d }; /^$/,$ { d }' Makefile.am | sed 's/^\s*//;s/[ ]*\\\\//' | tr '\n' ' '`;

for SUBDIR in ${SUBDIRS};
do
	if test ! -f ${SUBDIR}/Makefile.bcc;
	then
		continue;
	fi

	cat >> make.bat <<EOT
cd ${SUBDIR}
make.exe -fMakefile.bcc
cd ..

EOT

	cat >> make_clean.bat <<EOT
cd ${SUBDIR}
make.exe -fMakefile.bcc clean
cd ..

EOT
done

exit ${EXIT_SUCCESS};

