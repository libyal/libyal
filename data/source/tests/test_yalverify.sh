#!/bin/bash
# Verify tool testing script
#
# Version: 20200705

EXIT_SUCCESS=0;
EXIT_FAILURE=1;
EXIT_IGNORE=77;

OPTION_SETS="${tests_verify_tool_option_sets}";
OPTIONS=(${tests_verify_tool_options});

INPUT_GLOB="${tests_input_glob}";

if test -n "$${SKIP_TOOLS_TESTS}" || test -n "$${SKIP_TOOLS_END_TO_END_TESTS}";
then
	exit $${EXIT_IGNORE};
fi

TEST_EXECUTABLE="../${library_name_suffix}tools/${library_name_suffix}verify";

if ! test -x "$${TEST_EXECUTABLE}";
then
	TEST_EXECUTABLE="../${library_name_suffix}tools/${library_name_suffix}verify.exe";
fi

if ! test -x "$${TEST_EXECUTABLE}";
then
	echo "Missing test executable: $${TEST_EXECUTABLE}";

	exit $${EXIT_FAILURE};
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

if ! test -d "input";
then
	echo "Test input directory not found.";

	exit $${EXIT_IGNORE};
fi
RESULT=`ls input/* | tr ' ' '\n' | wc -l`;

if test $${RESULT} -eq $${EXIT_SUCCESS};
then
	echo "No files or directories found in the test input directory";

	exit $${EXIT_IGNORE};
fi

TEST_PROFILE_DIRECTORY=$$(get_test_profile_directory "input" "${library_name_suffix}verify");

IGNORE_LIST=$$(read_ignore_list "$${TEST_PROFILE_DIRECTORY}");

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

	TEST_SET_DIRECTORY=$$(get_test_set_directory "$${TEST_PROFILE_DIRECTORY}" "$${TEST_SET_INPUT_DIRECTORY}");

	OLDIFS=$${IFS};

	# IFS="\n"; is not supported by all platforms.
	IFS="
";

	if test -f "$${TEST_SET_DIRECTORY}/files";
	then
		for INPUT_FILE in `cat $${TEST_SET_DIRECTORY}/files | sed "s?^?$${TEST_SET_INPUT_DIRECTORY}/?"`;
		do
			run_test_on_input_file_with_options "$${TEST_SET_DIRECTORY}" "${library_name_suffix}verify" "with_stdout_reference" "$${OPTION_SETS}" "$${TEST_EXECUTABLE}" "$${INPUT_FILE}" "$${OPTIONS[@]}";
			RESULT=$$?;

			if test $${RESULT} -ne $${EXIT_SUCCESS};
			then
				break;
			fi
		done
	else
		for INPUT_FILE in `ls -1d $${TEST_SET_INPUT_DIRECTORY}/$${INPUT_GLOB}`;
		do
			run_test_on_input_file_with_options "$${TEST_SET_DIRECTORY}" "${library_name_suffix}verify" "with_stdout_reference" "$${OPTION_SETS}" "$${TEST_EXECUTABLE}" "$${INPUT_FILE}" "$${OPTIONS[@]}";
			RESULT=$$?;

			if test $${RESULT} -ne $${EXIT_SUCCESS};
			then
				break;
			fi
		done
	fi
	IFS=$${OLDIFS};

	if test $${RESULT} -ne $${EXIT_SUCCESS};
	then
		break;
	fi
done

exit $${RESULT};

