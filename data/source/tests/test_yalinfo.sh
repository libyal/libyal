#!/usr/bin/env bash
# Info tool testing script
#
# Version: 20231002

EXIT_SUCCESS=0;
EXIT_FAILURE=1;
EXIT_IGNORE=77;

PROFILES=(${tests_info_tool_profiles});
OPTIONS_PER_PROFILE=(${tests_info_tool_options_per_profile});
OPTION_SETS=(${tests_info_tool_option_sets});

INPUT_GLOB="${tests_info_tool_input_glob}";

if test -n "$${SKIP_TOOLS_TESTS}" || test -n "$${SKIP_TOOLS_END_TO_END_TESTS}";
then
	exit $${EXIT_IGNORE};
fi

TEST_EXECUTABLE="../${library_name_suffix}tools/${library_name_suffix}info";

if ! test -x "$${TEST_EXECUTABLE}";
then
	TEST_EXECUTABLE="../${library_name_suffix}tools/${library_name_suffix}info.exe";
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

for PROFILE_INDEX in $${!PROFILES[*]};
do
	TEST_PROFILE=$${PROFILES[$${PROFILE_INDEX}]};

	TEST_PROFILE_DIRECTORY=$$(get_test_profile_directory "input" "$${TEST_PROFILE}");

	IGNORE_LIST=$$(read_ignore_list "$${TEST_PROFILE_DIRECTORY}");

	IFS=" " read -a OPTIONS <<< $${OPTIONS_PER_PROFILE[$${PROFILE_INDEX}]};

	RESULT=$${EXIT_SUCCESS};

	for TEST_SET_INPUT_DIRECTORY in input/*;
	do
		if ! test -d "$${TEST_SET_INPUT_DIRECTORY}";
		then
			continue;
		fi
		TEST_SET=`basename $${TEST_SET_INPUT_DIRECTORY}`;

		if check_for_test_set_in_ignore_list "$${TEST_SET}" "$${IGNORE_LIST}";
		then
			continue;
		fi
		TEST_SET_DIRECTORY=$$(get_test_set_directory "$${TEST_PROFILE_DIRECTORY}" "$${TEST_SET_INPUT_DIRECTORY}");

		RESULT=$${EXIT_SUCCESS};

		if test -f "$${TEST_SET_DIRECTORY}/files";
		then
			IFS=$$'\n' INPUT_FILES=( $$(cat $${TEST_SET_DIRECTORY}/files | sed "s?^?$${TEST_SET_INPUT_DIRECTORY}/?") );
		else
			IFS=$$'\n' INPUT_FILES=( $$(ls -1d $${TEST_SET_INPUT_DIRECTORY}/$${INPUT_GLOB}) );
		fi
		for INPUT_FILE in $${INPUT_FILES[@]};
		do
			TESTED_WITH_OPTIONS=0;

			for OPTION_SET in $${OPTION_SETS[@]};
			do
				TEST_DATA_OPTION_FILE=$$(get_test_data_option_file "$${TEST_SET_DIRECTORY}" "$${INPUT_FILE}" "$${OPTION_SET}");

				if test -f $${TEST_DATA_OPTION_FILE};
				then
					TESTED_WITH_OPTIONS=1;

					run_test_on_input_file "$${TEST_SET_DIRECTORY}" "${library_name_suffix}info" "with_stdout_reference" "$${OPTION_SET}" "$${TEST_EXECUTABLE}" "$${INPUT_FILE}";
					RESULT=$$?;

					if test $${RESULT} -ne $${EXIT_SUCCESS};
					then
						break;
					fi
				fi
			done

			if $${TESTED_WITH_OPTIONS} -eq 0;
			then
				run_test_on_input_file "$${TEST_SET_DIRECTORY}" "${library_name_suffix}info" "with_stdout_reference" "" "$${TEST_EXECUTABLE}" "$${INPUT_FILE}";
				RESULT=$$?;
			fi

			# Ignore failures due to corrupted data.
			if test "$${TEST_SET}" = "corrupted";
			then
				RESULT=$${EXIT_SUCCESS};
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
done

exit $${RESULT};

