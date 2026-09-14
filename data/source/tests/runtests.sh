#!/bin/sh
# Script to run tests
#
# Version: 20260714

if [ -f "$${PWD}/${library_name}/.libs/${library_name}.1.dylib" ] && [ -f ./py${library_name_suffix}/.libs/py${library_name_suffix}.so ]
then
    install_name_tool -change /usr/local/lib/${library_name}.1.dylib "$${PWD}/${library_name}/.libs/${library_name}.1.dylib" ./py${library_name_suffix}/.libs/py${library_name_suffix}.so
fi

make check-build > /dev/null

# shellcheck disable=SC2068
make check $$@
RESULT=$$?

if [ $${RESULT} -ne 0 ]
then
    find . -name \*.log -path \*.dir/\*/\*.log -print -exec cat {} \;
fi
exit $${RESULT}

