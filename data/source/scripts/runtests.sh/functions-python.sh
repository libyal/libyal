run_setup_py_tests()
{
	# Skip this test when running Cygwin on AppVeyor.
	if test -n "$${APPVEYOR}" && test $${TARGET} = "cygwin";
	then
		echo "Running: 'setup.py build' skipped";

		return $${EXIT_SUCCESS};
	fi
	PYTHON=$$1;

	$${PYTHON} setup.py build;
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		echo "Running: 'setup.py build' failed";

		return $${RESULT};
	fi
	return $${EXIT_SUCCESS};
}

