if test $${HAVE_ENABLE_VERBOSE_OUTPUT} -eq 0 && test $${HAVE_ENABLE_DEBUG_OUTPUT} -eq 0;
then
	# Test "./configure && make && make check" with verbose and debug output.

	run_configure_make_check "--enable-verbose-output --enable-debug-output";
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		exit $${EXIT_FAILURE};
	fi
fi

