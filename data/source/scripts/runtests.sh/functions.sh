run_configure_make()
{
	local CONFIGURE_OPTIONS=$$@;

	./configure $${CONFIGURE_OPTIONS[@]};
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		echo "Running: './configure' failed";

		return $${RESULT};
	fi

	make clean > /dev/null;
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		echo "Running: 'make clean' failed";

		return $${RESULT};
	fi

	make > /dev/null;
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		echo "Running: 'make' failed";

		return $${RESULT};
	fi
	return $${EXIT_SUCCESS};
}

run_configure_make_check()
{
	run_configure_make $$@;
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		return $${RESULT};
	fi

	make check CHECK_WITH_STDERR=1;
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		echo "Running: 'make check' failed";

		if test -f tests/test-suite.log;
		then
			cat tests/test-suite.log;
		fi

		return $${RESULT};
	fi
	return $${EXIT_SUCCESS};
}

run_configure_make_check_with_asan()
{
	local LDCONFIG=`which ldconfig 2> /dev/null`;

	if test -z $${LDCONFIG} || test ! -x $${LDCONFIG};
	then
		return $${EXIT_SUCCESS};
	fi
	local LIBASAN=`ldconfig -p | grep libasan | sed 's/^.* => //' | sort | tail -n 1`;

	if test -z $${LIBASAN} || test ! -f $${LIBASAN};
	then
		return $${EXIT_SUCCESS};
	fi
	# Using libasan is platform dependent.
	if test $${LIBASAN} != "/lib64/libasan.so.4" && test $${LIBASAN} != "/lib64/libasan.so.5";
	then
		return $${EXIT_SUCCESS};
	fi

	export CPPFLAGS="-DHAVE_ASAN";
	export CFLAGS="-fno-omit-frame-pointer -fsanitize=address -g";
	export LDFLAGS="-fsanitize=address -g";

	if test -z $${CC} || test $${CC} != "clang";
	then
		LDFLAGS="$${LDFLAGS} -lasan";
	fi

	run_configure_make $$@;
	RESULT=$$?;

	export CPPFLAGS=;
	export CFLAGS=;
	export LDFLAGS=;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		return $${RESULT};
	fi

	make check CHECK_WITH_ASAN=1 CHECK_WITH_STDERR=1;
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		echo "Running: 'make check' failed";

		if test -f tests/test-suite.log;
		then
			cat tests/test-suite.log;
		fi

		return $${RESULT};
	fi
	return $${RESULT};
}

run_configure_make_check_with_coverage()
{
	# Disable optimization so we can hook malloc and realloc.
	export CPPFLAGS="-DOPTIMIZATION_DISABLED";
	export CFLAGS="--coverage -O0";
	export LDFLAGS="--coverage";

	# Disable creating a shared library so we can hook memset.
	run_configure_make_check $$@;
	RESULT=$$?;

	export CPPFLAGS=;
	export CFLAGS=;
	export LDFLAGS=;

	return $${RESULT};
}

run_configure_make_check_python()
{
	run_configure_make $$@;
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		return $${RESULT};
	fi

	make check CHECK_WITH_STDERR=1 SKIP_LIBRARY_TESTS=1 SKIP_TOOLS_TESTS=1;
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		echo "Running: 'make check' failed";

		if test -f tests/test-suite.log;
		then
			cat tests/test-suite.log;
		fi

		return $${RESULT};
	fi
	return $${EXIT_SUCCESS};
}

