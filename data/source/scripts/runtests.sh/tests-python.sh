# Test "./configure && make && make check" to build Python bindings.

PYTHON_CONFIG="";

if test -x /usr/bin/whereis;
then
	PYTHON_CONFIG=`/usr/bin/whereis python-config | sed 's/^.*:[ ]*//' 2> /dev/null`;
fi

# Test with Python 2.
PYTHON2=`which python2 2> /dev/null`;

# Note that "test -x" on Mac OS X will succeed if the argument is not set.
if test -n "$${PYTHON2}" && test -x $${PYTHON2};
then
	export PYTHON_VERSION=2;

	run_configure_make_check_python "--enable-python";
	RESULT=$$?;

	export PYTHON_VERSION=;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		exit $${EXIT_FAILURE};
	fi
	export PYTHON_VERSION=2;

	run_configure_make_check_python "--enable-python2";
	RESULT=$$?;

	export PYTHON_VERSION=;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		exit $${EXIT_FAILURE};
	fi

	if test -f "setup.py" && ! run_setup_py_tests $${PYTHON2};
	then
		exit $${EXIT_FAILURE};
	fi
fi

# Test with Python 3.
PYTHON3=`which python3 2> /dev/null`;

# Note that "test -x" on Mac OS X will succeed if the argument is not set.
if test -n "$${PYTHON3}" && test -x $${PYTHON3};
then
	export PYTHON_VERSION=3;

	run_configure_make_check_python "--enable-python";
	RESULT=$$?;

	export PYTHON_VERSION=;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		exit $${EXIT_FAILURE};
	fi
	export PYTHON_VERSION=3;

	run_configure_make_check_python "--enable-python3";
	RESULT=$$?;

	export PYTHON_VERSION=;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		exit $${EXIT_FAILURE};
	fi

	if test -f "setup.py" && ! run_setup_py_tests $${PYTHON3};
	then
		exit $${EXIT_FAILURE};
	fi
fi

# Test with the default Python version.
if test -z $${PYTHON2} && test -z $${PYTHON3};
then
	run_configure_make_check_python "--enable-python";
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		exit $${EXIT_FAILURE};
	fi

	PYTHON=`which python 2> /dev/null`;

	if test -f "setup.py" && ! run_setup_py_tests $${PYTHON};
	then
		exit $${EXIT_FAILURE};
	fi
fi

