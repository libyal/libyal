#!/bin/bash
# Library API type testing script
#
# Version: 20160327

EXIT_SUCCESS=0;
EXIT_FAILURE=1;
EXIT_IGNORE=77;

TEST_PREFIX=`dirname $${PWD}`;
TEST_PREFIX=`basename $${TEST_PREFIX} | sed 's/^lib\([^-]*\).*$$/\1/'`;
TEST_TYPES="${library_public_types}";

TEST_PROFILE="lib$${TEST_PREFIX}";

TEST_TOOL_DIRECTORY=".";

test_api_type()
{
	local TEST_TYPE=$$1;

	local TEST_TOOL="$${TEST_PREFIX}_test_$${TEST_TYPE}";
	local TEST_EXECUTABLE="$${TEST_TOOL_DIRECTORY}/$${TEST_TOOL}";

	if ! test -x "$${TEST_EXECUTABLE}";
	then
		TEST_EXECUTABLE="$${TEST_TOOL_DIRECTORY}/$${TEST_TOOL}.exe";
	fi

	if ! test -x "$${TEST_EXECUTABLE}";
	then
		echo "Missing test executable: $${TEST_EXECUTABLE}";

		exit $${EXIT_FAILURE};
	fi
	echo "Testing API type: lib$${TEST_PREFIX}_$${TEST_TYPE}_t";

	run_test_with_arguments $${TEST_EXECUTABLE};
	local RESULT=$$?;

	echo "";

	return $${RESULT};
}

if ! test -z $${SKIP_LIBRARY_TESTS};
then
	exit $${EXIT_IGNORE};
fi

TEST_RUNNER="tests/test_runner.sh";

if ! test -f "$${TEST_RUNNER}";
then
	TEST_RUNNER="./test_runner.sh";
fi

if ! test -f "$${TEST_RUNNER}";
then
	echo "Missing test runner: $${TEST_RUNNER}";

	exit $${EXIT_FAILURE};
fi

source $${TEST_RUNNER};

for TEST_TYPE in $${TEST_TYPES};
do
	test_api_type "$${TEST_TYPE}";
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		break;
	fi
done

exit $${RESULT};

