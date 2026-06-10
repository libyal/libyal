#!/bin/sh
# Script to run tests
#
# Version: 20260609

if test -f $${PWD}/${library_name}/.libs/${library_name}.1.dylib && test -f ./py${library_name_suffix}/.libs/py${library_name_suffix}.so
then
	install_name_tool -change /usr/local/lib/${library_name}.1.dylib $${PWD}/${library_name}/.libs/${library_name}.1.dylib ./py${library_name_suffix}/.libs/py${library_name_suffix}.so
fi

make check-build > /dev/null

make check $$@
RESULT=$$?

if test $${RESULT} -ne 0
then
	find . -name \*.log -path \*.dir/\*/\*.log -print -exec cat {} \;
fi
exit $${RESULT}

