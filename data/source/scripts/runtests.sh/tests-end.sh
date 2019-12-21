# Run tests with asan.

CONFIGURE_OPTIONS="${asan_configure_options}";

if test $${HAVE_ENABLE_WIDE_CHARACTER_TYPE} -eq 0;
then
	CONFIGURE_OPTIONS="$${CONFIGURE_OPTIONS} --enable-wide-character-type";
fi

run_configure_make_check_with_asan $${CONFIGURE_OPTIONS};
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

# Run tests with coverage.

CONFIGURE_OPTIONS="${coverage_configure_options}";

if test $${HAVE_ENABLE_WIDE_CHARACTER_TYPE} -eq 0;
then
	CONFIGURE_OPTIONS="$${CONFIGURE_OPTIONS} --enable-wide-character-type";
fi

run_configure_make_check_with_coverage $${CONFIGURE_OPTIONS};
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

exit $${EXIT_SUCCESS};

