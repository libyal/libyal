if test $${HAVE_WITH_PTHREAD} -eq 0;
then
	# Test "./configure && make && make check" without multi-threading support.

	run_configure_make_check "--with-pthread=no";
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		exit $${EXIT_FAILURE};
	fi
fi

