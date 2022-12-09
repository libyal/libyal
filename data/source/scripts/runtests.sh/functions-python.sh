run_setup_py_tests()
{
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

