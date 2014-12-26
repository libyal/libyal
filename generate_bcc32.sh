#!/bin/bash
#
# Script to generate the Borland's C++ Compiler 5.5 Makefiles
#
# Copyright (c) 2014, Joachim Metz <joachim.metz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

EXIT_SUCCESS=0;
EXIT_FAILURE=1;

for DIRECTORY in lib*;
do
	if test ! -d ${DIRECTORY};
	then
		continue;
	fi
	if test ! -f ${DIRECTORY}/Makefile.am;
	then
		continue;
	fi
	AM_CPPFLAGS=`sed '/^if / { d }; /^AM_CPPFLAGS =/ { d }; /^$/,$ { d }' ${DIRECTORY}/Makefile.am | sed 's/^\s*//;s/ \\\\//' | tr '\n' ' '`;
	SOURCES=`sed '/^if / { d }; /^AM_CPPFLAGS =/,/_la_SOURCES =/ { d }; /^endif$/ { d }; /^$/,$ { d }' ${DIRECTORY}/Makefile.am | sed 's/^\s*//;s/ \\\\//' | tr '\n' ' '`;
	LIBADD=`sed '/^if / { d }; /^AM_CPPFLAGS =/,/_la_LIBADD =/ { d }; /^endif$/ { d }; /^$/,$ { d }' ${DIRECTORY}/Makefile.am | sed 's/^\s*//;s/ \\\\//' | tr '\n' ' '`;

	grep '_la_LDFLAGS' ${DIRECTORY}/Makefile.am 2> /dev/null;
	SHARED_LIBRARY=$?;

	# Determine the include directories.
	INCLUDES=`echo ${AM_CPPFLAGS} | tr ' ' '\n' | grep -e '^@LIB[^_]*_CPPFLAGS@$' | sed 's/^@\([^_]*\)_CPPFLAGS@$/..\\\\\1/' | tr '[A-Z]' '[a-z]' | tr '\n' ';'`;

	# Determine the definitions.
	DEFINITIONS_PART1=`echo ${AM_CPPFLAGS} | tr ' ' '\n' | grep -e '@LIB[^_]*_CPPFLAGS@' | sed 's/^@\([^_]*\)_CPPFLAGS@$/-DHAVE_LOCAL_\1/' | tr '\n' ' '`;

	if test ${SHARED_LIBRARY} -eq 0;
	then
		DEFINITIONS_PART2=`echo -D${DIRECTORY}_DLL_EXPORT | tr '[a-z]' '[A-Z]'`;
	else
		DEFINITIONS_PART2=`echo -DHAVE_LOCAL_${DIRECTORY} | tr '[a-z]' '[A-Z]'`;
	fi
	DEFINITIONS="${DEFINITIONS_PART1}${DEFINITIONS_PART2}";

	# Determine the source files.
	SOURCE_FILES=`echo ${SOURCES} | tr ' ' '\n' | grep -e '.c$' | tr '\n' ' '`;

	# Determine the library dependencies. 
	LIBRARIES=`echo ${LIBADD} | tr ' ' '\n' | grep -e '@LIB[^_]*_LIBADD@' | sed 's/^@\([^_]*\)_LIBADD@$/..\\\\\1\\\\\1.lib/' | tr '[A-Z]' '[a-z]' | tr '\n' ' '`;

	if test ${SHARED_LIBRARY} -eq 0;
	then
		TARGET="${DIRECTORY}.dll";
	else
		TARGET="${DIRECTORY}.lib";
	fi
	# Note that since Borland's C++ Compiler 5.5 defines memory.h and thus
	# ..\common must be included before $(BCCDIR)\Include

	cat > ${DIRECTORY}/Makefile.bcc <<EOT
# Borland's C++ Compiler 5.5 Makefile

BCC32    = bcc32
CPP32    = cpp32
ILINK32  = ilink32
TLIB     = tlib
RM       = del
BCCDIR   = C:\\Borland\\BCC55

CFLAGS   = -5 -O2 -w-aus -w-ccc -w-csu -w-par -w-pia -w-rch -w-inl -w-ngu -w-pro
LDFLAGS  = -aa -V4.0 -c -x -Gn
DEFS     = -DNDEBUG -DWIN32 -DCONSOLE ${DEFINITIONS}
INCLUDES = -I..\\include;..\\common;${INCLUDES}.;\$(BCCDIR)\\Include;

LIBADD   = ${LIBRARIES}

TARGET   = ${TARGET}

SOURCES  = ${SOURCE_FILES}

OBJECTS  = \$(SOURCES:.c=.obj)

.SUFFIXES: .c

.c.obj:
	\$(BCC32) -c \$(INCLUDES) \$(CFLAGS) \$(DEFS) \$<

all:	\$(TARGET)

clean:
	\$(RM) *.lib *.obj

\$(TARGET): \$(LIBADD) \$(OBJECTS)
	\$(RM) \$(TARGET)
EOT

	if test ${SHARED_LIBRARY} -eq 0;
	then
		cat >> ${DIRECTORY}/Makefile.bcc <<EOT
	\$(ILINK32) -Tpd -j\$(BCCDIR)\\Lib -L\$(BCCDIR)\\Lib \$(LDFLAGS) \$(OBJECTS), \$(TARGET), , \$(LIBADD) import32.lib cw32.lib, ,
EOT
	else
		cat >> ${DIRECTORY}/Makefile.bcc <<EOT
	\$(TLIB) \$(TARGET)
EOT
	fi

done

# Create make.bat to recursively build all the libraries and DLL.
rm -f make.bat;

SUBDIRS=`sed '/^ACLOCAL_AMFLAGS =/,/^SUBDIRS =/ { d }; /^$/,$ { d }' Makefile.am | sed 's/^\s*//;s/ \\\\//' | tr '\n' ' '`;

for SUBDIR in ${SUBDIRS};
do
	if test ${SUBDIR} = "include" || test ${SUBDIR} = "common";
	then
		continue;
	fi

	cat >> make.bat <<EOT
cd ${SUBDIR}
c:\\Borland\\BCC55\\Bin\\make.exe -fMakefile.bcc
cd ..

EOT

	if test -f ${SUBDIR}/${SUBDIR}.rc;
	then
		cat >> make.bat <<EOT
move ${SUBDIR}\\${SUBDIR}.dll .
EOT

		break;
	fi
done

