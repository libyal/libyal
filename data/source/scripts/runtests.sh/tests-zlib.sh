# Test "./configure && make && make check" with fallback zlib implementation.

run_configure_make_check "--with-zlib=no";
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

