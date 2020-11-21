#!/bin/sh
# Script to run tests
#
# Version: 20201121

if test -f $${PWD}/${library_name}/.libs/${library_name}.1.dylib && test -f ./py${library_name_suffix}/.libs/py${library_name_suffix}.so;
then
	install_name_tool -change /usr/local/lib/${library_name}.1.dylib $${PWD}/${library_name}/.libs/${library_name}.1.dylib ./py${library_name_suffix}/.libs/py${library_name_suffix}.so;
fi

make check CHECK_WITH_STDERR=1;
RESULT=$$?;

if test $${RESULT} -ne 0 && test -f tests/test-suite.log;
then
	cat tests/test-suite.log;
fi
exit $${RESULT};

