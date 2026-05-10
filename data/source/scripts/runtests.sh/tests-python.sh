# Test "./configure && make && make check" to build Python bindings.

PYTHON_CONFIG="";

if test -x /usr/bin/whereis;
then
	PYTHON_CONFIG=`/usr/bin/whereis python-config | sed 's/^.*:[ ]*//' 2> /dev/null`;
fi

run_configure_make_check_python "--enable-python";
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

