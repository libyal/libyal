# Test "./configure && make && make check" without options.

run_configure_make_check;
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

