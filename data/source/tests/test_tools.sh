#!/usr/bin/env bash
# Tests tools functions and types.
#
# Version: 20231001

EXIT_SUCCESS=0;
EXIT_FAILURE=1;
EXIT_IGNORE=77;

TOOLS_TESTS="${tools_tests}";
TOOLS_TESTS_WITH_INPUT="${tools_tests_with_input}";
OPTION_SETS=(${tests_option_sets});

INPUT_GLOB="${tests_input_glob}";

run_test()
{
	local TEST_NAME=$$1;

	local TEST_DESCRIPTION="Testing: $${TEST_NAME}";
	local TEST_EXECUTABLE="./${library_name_suffix}_test_tools_$${TEST_NAME}";

	if ! test -x "$${TEST_EXECUTABLE}";
	then
		TEST_EXECUTABLE="$${TEST_EXECUTABLE}.exe";
	fi

	# TODO: add support for TEST_PROFILE and OPTION_SETS?
	run_test_with_arguments "$${TEST_DESCRIPTION}" "$${TEST_EXECUTABLE}";
	local RESULT=$$?;

	return $${RESULT};
}

run_test_with_input()
{
	local TEST_NAME=$$1;

	local TEST_DESCRIPTION="Testing: $${TEST_NAME}";
	local TEST_EXECUTABLE="./${library_name_suffix}_test_tools_$${TEST_NAME}";

	if ! test -x "$${TEST_EXECUTABLE}";
	then
		TEST_EXECUTABLE="$${TEST_EXECUTABLE}.exe";
	fi

	if ! test -d "input";
	then
		echo "Test input directory not found.";

		return $${EXIT_IGNORE};
	fi
	local RESULT=`ls input/* | tr ' ' '\n' | wc -l`;

	if test $${RESULT} -eq $${EXIT_SUCCESS};
	then
		echo "No files or directories found in the test input directory";

		return $${EXIT_IGNORE};
	fi

	local TEST_PROFILE_DIRECTORY=$$(get_test_profile_directory "input" "${library_name_suffix}tools");

	local IGNORE_LIST=$$(read_ignore_list "$${TEST_PROFILE_DIRECTORY}");

	RESULT=$${EXIT_SUCCESS};

	for TEST_SET_INPUT_DIRECTORY in input/*;
	do
		if ! test -d "$${TEST_SET_INPUT_DIRECTORY}";
		then
			continue;
		fi
		if check_for_directory_in_ignore_list "$${TEST_SET_INPUT_DIRECTORY}" "$${IGNORE_LIST}";
		then
			continue;
		fi

		local TEST_SET_DIRECTORY=$$(get_test_set_directory "$${TEST_PROFILE_DIRECTORY}" "$${TEST_SET_INPUT_DIRECTORY}");

		if test -f "$${TEST_SET_DIRECTORY}/files";
		then
			IFS=$$'\n' read -a INPUT_FILES <<< $$(cat $${TEST_SET_DIRECTORY}/files | sed "s?^?$${TEST_SET_INPUT_DIRECTORY}/?");
		else
			IFS=$$'\n' read -a INPUT_FILES <<< $$(ls -1d $${TEST_SET_INPUT_DIRECTORY}/$${INPUT_GLOB});
		fi
		for INPUT_FILE in "$${INPUT_FILES[@]}";
		do
			if test "$${OSTYPE}" = "msys";
			then
				# A test executable built with MinGW expects a Windows path.
				INPUT_FILE=`echo $${INPUT_FILE} | sed 's?/?\\\\?g'`;
			fi
			local TESTED_WITH_OPTIONS=0;

			for OPTION_SET in $${OPTION_SETS[@]};
			do
				local TEST_DATA_OPTION_FILE=$$(get_test_data_option_file "$${TEST_SET_DIRECTORY}" "$${INPUT_FILE}" "$${OPTION_SET}");

				if test -f $${TEST_DATA_OPTION_FILE};
				then
					TESTED_WITH_OPTIONS=1;

					IFS=" " read -a OPTIONS <<< $$(read_test_data_option_file "$${TEST_SET_DIRECTORY}" "$${INPUT_FILE}" "$${OPTION_SET}");

					run_test_on_input_file "$${TEST_SET_DIRECTORY}" "$${TEST_DESCRIPTION}" "default" "$${OPTION_SET}" "$${TEST_EXECUTABLE}" "$${INPUT_FILE}" "$${OPTIONS[@]}";
					RESULT=$$?;

					if test $${RESULT} -ne $${EXIT_SUCCESS};
					then
						break;
					fi
				fi
			done

			if test $${TESTED_WITH_OPTIONS} -eq 0;
			then
				run_test_on_input_file "$${TEST_SET_DIRECTORY}" "$${TEST_DESCRIPTION}" "default" "" "$${TEST_EXECUTABLE}" "$${INPUT_FILE}";
				RESULT=$$?;
			fi

			if test $${RESULT} -ne $${EXIT_SUCCESS};
			then
				break;
			fi
		done

		if test $${RESULT} -ne $${EXIT_SUCCESS};
		then
			break;
		fi
	done

	return $${RESULT};
}

if test -n "$${SKIP_TOOLS_TESTS}";
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

RESULT=$${EXIT_IGNORE};

for TEST_NAME in $${TOOLS_TESTS};
do
	run_test "$${TEST_NAME}";
	RESULT=$$?;

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		break;
	fi
done

if test $${RESULT} -ne $${EXIT_SUCCESS} && test $${RESULT} -ne $${EXIT_IGNORE};
then
	exit $${RESULT};
fi

for TEST_NAME in $${TOOLS_TESTS_WITH_INPUT};
do
	if test -d "input";
	then
		run_test_with_input "$${TEST_NAME}";
		RESULT=$$?;
	else
		run_test "$${TEST_NAME}";
		RESULT=$$?;
	fi

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		break;
	fi
done

exit $${RESULT};

