# Test "./configure && make && make check" to build static executables.

run_configure_make_check "--enable-static-executables";
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

