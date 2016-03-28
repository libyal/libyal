#!/bin/bash
# Bash functions to run an executable for testing.
#
# Version: 20160328
#
# When CHECK_WITH_GDB is set to a non-empty value the test executable
# is run with gdb, otherwise it is run without.
#
# When CHECK_WITH_REFERENCE_FILE is set to a non-empty value the output
# of the test executable is compared to a previously stored reference file
# if available, otherwise the output is stored as the reference file.
# The first 2 lines of the output are ignored.
#
# When CHECK_WITH_VALGRIND is set to a non-empty value the test executable
# is run with valgrind, otherwise it is run without.

EXIT_SUCCESS=0;
EXIT_FAILURE=1;
EXIT_IGNORE=77;

# Checks the availability of a binary.
#
# Arguments:
#   a string containing the name of the binary
#
check_availability_binary()
{
	local BINARY=$1;

	which ${BINARY} > /dev/null 2>&1;
	if test $? -ne 0;
	then
		echo "Missing binary: ${BINARY}";
		echo "";

		exit ${EXIT_FAILURE};
	fi
}

# Checks if the input directory is in the ignore list.
#
# Arguments:
#   a string containing the path of the test input directory
#   a string containing space separated ignore list
#
# Returns:
#   an integer containing the exit status to indicate the input directory
#   was found in the ignore list.
#
check_for_directory_in_ignore_list()
{
	local INPUT_DIRECTORY=$1;
	local IGNORE_LIST=$@;

	local INPUT_BASENAME=`basename ${INPUT_DIRECTORY}`;

	for LIST_ELEMENT in `echo "${IGNORE_LIST}" | tr ' ' '\n'`;
	do
		if test "${LIST_ELEMENT}" = "${INPUT_BASENAME}";
		then
			return ${EXIT_SUCCESS};
		fi
	done
	return ${EXIT_FAILURE};
}

# Searches for the binary variant of the executable in case the test executable
# refers to a libtool shell script.
#
# Arguments:
#   a string containing the path of the test executable
#
# Returns:
#   a string containing the path of the binary variant of the test executable
#
find_binary_executable()
{
	local TEST_EXECUTABLE=$1;

	file -bi ${TEST_EXECUTABLE} | sed 's/;.*$//' | grep "text/x-shellscript" > /dev/null 2>&1;

	echo ${TEST_EXECUTABLE} | grep 'tools' > /dev/null 2>&1;

	if test $? -eq 0;
	then
		TEST_EXECUTABLE=`readlink -f ${TEST_EXECUTABLE}`;

		if ! test -x ${TEST_EXECUTABLE};
		then
			echo "Unable to find test executable: ${TEST_EXECUTABLE}";

			exit ${EXIT_FAILURE};
		fi

		file -bi ${TEST_EXECUTABLE} | sed 's/;.*$//' | grep "application/x-executable" > /dev/null 2>&1;

		if test $? -ne 0;
		then
			echo "Invalid test executable: ${TEST_EXECUTABLE}";

			exit ${EXIT_FAILURE};
		fi
	fi
	return ${TEST_EXECUTABLE};
}

# Searches for the path to the binary variant of the library.
#
# Arguments:
#   a string containing the path of the test executable
#
# Returns:
#   a string containing the path of the binary variant of the library.
#
find_binary_library_path()
{
	local TEST_EXECUTABLE=$1;

	# TODO: improve.
	if test $? -eq 0;
	then
		LIBRARY=`dirname ${TEST_EXECUTABLE} | sed 's?.*/\(.*\)tools$?lib\1?'`;
	else
		LIBRARY=`basename ${TEST_EXECUTABLE} | sed 's/^\(.*\)_test_.*$/lib\1/'`;
	fi
	return ${LIBRARY};
}

# Determines the test input files.
#
# Arguments:
#   a string containing the path of the test input directory
#   a string containing the path of the test set input directory
#   a string containing the input glob
#
# Returns:
#   a string containing the test input files
#
get_test_input_files()
{
	local INPUT_DIRECTORY=$1;
	local TEST_SET_INPUT_DIRECTORY=$2;
	local INPUT_GLOB=$3;

	local INPUT_FILES="";

	if test -f "${TEST_SET_INPUT_DIRECTORY}/files";
	then
		INPUT_FILES=`cat ${TEST_SET_INPUT_DIRECTORY}/files | sed "s?^?${INPUT_DIRECTORY}/?"`;
	else
		INPUT_FILES=`ls ${INPUT_DIRECTORY}/${INPUT_GLOB}`;
	fi
	echo "${INPUT_FILES}";
}

# Determines the test option file.
#
# Arguments:
#   a string containing the path of the test set directory
#   a string containing the path of the test input file
#   a string containing the name of the option set
#
# Returns:
#   a string containing the test input files
#
get_testion_option_file()
{
	local TEST_SET_DIRECTORY=$1;
	local INPUT_FILE=$2;
	local OPTION_SET=$3;

	local INPUT_NAME=`basename ${INPUT_FILE}`;
	local OPTION_FILE="${TEST_SET_DIRECTORY}/${INPUT_NAME}.${OPTION_SET}";

	echo "${OPTION_FILE}";
}

# Determines the test profile directory.
# The directory is created if it does not exist.
#
# Arguments:
#   a string containing the path of the test input directory
#   a string containing the name of the test profile
#
# Returns:
#   a string containing the path of the test profile directory
#
get_test_profile_directory()
{
	local TEST_INPUT_DIRECTORY=$1;
	local TEST_PROFILE=$2;

	local TEST_PROFILE_DIRECTORY="${TEST_INPUT_DIRECTORY}/.${TEST_PROFILE}";

	if ! test -d "${TEST_PROFILE_DIRECTORY}";
	then
		mkdir "${TEST_PROFILE_DIRECTORY}";
	fi
	echo "${TEST_PROFILE_DIRECTORY}";
}

# Determines the test set directory.
# The directory is created if it does not exist.
#
# Arguments:
#   a string containing the path of the test profile directory
#   a string containing the path of the test set input directory
#
# Returns:
#   a string containing the path of the test set directory
#
get_test_set_directory()
{
	local TEST_PROFILE_DIRECTORY=$1;
	local TEST_SET_INPUT_DIRECTORY=$2;

	local TEST_SET=`basename ${TEST_SET_INPUT_DIRECTORY}`;
	local TEST_SET_DIRECTORY="${TEST_PROFILE_DIRECTORY}/${TEST_SET}";

	if ! test -d "${TEST_SET_DIRECTORY}";
	then
		mkdir "${TEST_SET_DIRECTORY}";
	fi
	echo "${TEST_SET_DIRECTORY}";
}

# Reads the test profile ignore file if it exists
#
# Arguments:
#   a string containing the path of the test profile directory
#
# Returns:
#   a string containing a space separated ignore list
#
read_ignore_list()
{
	local TEST_PROFILE_DIRECTORY=$1;
	local IGNORE_FILE="${TEST_PROFILE_DIRECTORY}/ignore";
	local IGNORE_LIST="";

	if test -f "${IGNORE_FILE}";
	then
		IGNORE_LIST=`cat ${IGNORE_FILE} | sed '/^#/d'`;
	fi
	echo ${IGNORE_LIST};
}

# Reads the test set option file
#
# Arguments:
#   a string containing the path of the test set directory
#   a string containing the path of the test input file
#   a string containing the name of the option set
#
# Returns:
#   a string containing the ignore list
#
read_option_file()
{
	local TEST_SET_DIRECTORY=$1;
	local INPUT_FILE=$2;
	local OPTION_SET=$3;

	local OPTION_FILE=$(get_testion_option_file ${TEST_SET_DIRECTORY} ${INPUT_FILE} ${OPTION_SET});

	local OPTIONS=()
	local OPTIONS_STRING=`cat "${OPTION_FILE}" | head -n 1 | sed 's/[\r\n]*$//'`;
	IFS=" " read -a OPTIONS <<< ${OPTIONS_STRING};

	return ${OPTIONS[*]};
}

# Runs the test
#
# Globals:
#   CHECK_WITH_GDB
#   CHECK_WITH_VALGRIND
#
# Arguments:
#   a string containing the path of the test executable
#   an array containing the arguments for the test executable
#
# Returns:
#   an integer containg the exit status of the test executable
#
run_test_with_arguments()
{
	local TEST_EXECUTABLE=$1;
	shift 1;
	local ARGUMENTS=$@;

	local RESULT=0;

	if ! test -z ${CHECK_WITH_GDB};
	then
		LIBRARY=$( find_binary_library_path ${TEST_EXECUTABLE} );
		TEST_EXECUTABLE=$( find_binary_executable ${TEST_EXECUTABLE} );

		LD_LIBRARY_PATH="../${LIBRARY}/.libs/" gdb -ex r --args "${TEST_EXECUTABLE}" ${ARGUMENTS[*]};
		RESULT=$?;

	elif ! test -z ${CHECK_WITH_VALGRIND};
	then
		VALGRIND_LOG="valgrind.log-$$";

		LIBRARY=$( find_binary_library_path ${TEST_EXECUTABLE} );
		TEST_EXECUTABLE=$( find_binary_executable ${TEST_EXECUTABLE} );

		LD_LIBRARY_PATH="../${LIBRARY}/.libs/" valgrind --tool=memcheck --leak-check=full --track-origins=yes --show-reachable=yes --log-file=${VALGRIND_LOG} "${TEST_EXECUTABLE}" ${ARGUMENTS[*]};
		RESULT=$?;

		if test ${RESULT} -eq 0;
		then
			grep "All heap blocks were freed -- no leaks are possible" ${VALGRIND_LOG} > /dev/null 2>&1;

			if test $? -ne 0;
			then
				echo "Memory leakage detected.";

				cat ${VALGRIND_LOG};

				RESULT=${EXIT_FAILURE};
			fi
		fi
		rm -f ${VALGRIND_LOG};

	else
		${TEST_EXECUTABLE} ${ARGUMENTS[*]} 2> /dev/null;
		RESULT=$?;
	fi
	return ${RESULT};
}

# Runs the test on the input file
#
# Globals:
#   CHECK_WITH_GDB
#   CHECK_WITH_REFERENCE_FILE
#   CHECK_WITH_VALGRIND
#
# Arguments:
#   a string containing the path of the test set directory
#   a string containing the description of the test
#   a string containing the name of the option set
#   a string containing the path of the test executable
#   a string containing the path of the test input file
#   an array containing the arguments for the test executable
#
# Returns:
#   an integer containg the exit status of the test executable
#
run_test_on_input_file()
{
	local TEST_SET_DIRECTORY=$1;
	local TEST_DESCRIPTION=$2;
	local OPTION_SET=$3;
	local TEST_EXECUTABLE=$4;
	local INPUT_FILE=$5;
	shift 5;
	local ARGUMENTS=$@;

	local INPUT_NAME=`basename ${INPUT_FILE}`;
	local OPTIONS=();
	local TEST_OUTPUT="${INPUT_NAME}";

	if ! test -z "${OPTION_SET}";
	then
		read_option_file ${TEST_SET_DIRECTORY} ${INPUT_FILE} ${OPTION_SET};
		OPTIONS=$?;

		TEST_OUTPUT="${INPUT_NAME}-${OPTION_SET}";
	fi

	local TMPDIR="tmp$$";
	local RESULT=0;

	rm -rf ${TMPDIR};
	mkdir ${TMPDIR};

	if ! test -z ${CHECK_WITH_GDB};
	then
		LIBRARY=$( find_binary_library_path ${TEST_EXECUTABLE} );
		TEST_EXECUTABLE=$( find_binary_executable ${TEST_EXECUTABLE} );

		LD_LIBRARY_PATH="../${LIBRARY}/.libs/" gdb -ex r --args "${TEST_EXECUTABLE}" ${ARGUMENTS[*]} ${OPTIONS[*]} "${INPUT_FILE}";
		RESULT=$?;

	elif ! test -z ${CHECK_WITH_REFERENCE_FILE};
	then
		local TEST_RESULTS="${TMPDIR}/${TEST_OUTPUT}.log";

		${TEST_EXECUTABLE} ${ARGUMENTS[*]} ${OPTIONS[*]} ${INPUT_FILE} | sed '1,2d' > ${TEST_RESULTS};
		RESULT=$?;

		local STORED_TEST_RESULTS="${TEST_SET_DIRECTORY}/${TEST_OUTPUT}.log.gz";

		if test -f "${STORED_TEST_RESULTS}";
		then
			zcat ${STORED_TEST_RESULTS} | diff ${TEST_RESULTS} -;

			RESULT=$?;
		else
			gzip ${TEST_RESULTS};

			mv "${TEST_RESULTS}.gz" ${TEST_SET_DIRECTORY};
		fi

	elif ! test -z ${CHECK_WITH_VALGRIND};
	then
		VALGRIND_LOG="${TMPDIR}/valgrind.log";

		LIBRARY=$( find_binary_library_path ${TEST_EXECUTABLE} );
		TEST_EXECUTABLE=$( find_binary_executable ${TEST_EXECUTABLE} );

		LD_LIBRARY_PATH="../${LIBRARY}/.libs/" valgrind --tool=memcheck --leak-check=full --track-origins=yes --show-reachable=yes --log-file=${VALGRIND_LOG} "${TEST_EXECUTABLE}" ${ARGUMENTS[*]} ${OPTIONS[*]} "${INPUT_FILE}";
		RESULT=$?;

		if test ${RESULT} -eq 0;
		then
			grep "All heap blocks were freed -- no leaks are possible" ${VALGRIND_LOG} > /dev/null 2>&1;

			if test $? -ne 0;
			then
				echo "Memory leakage detected.";

				cat ${VALGRIND_LOG};

				RESULT=${EXIT_FAILURE};
			fi
		fi
		rm -f ${VALGRIND_LOG};

	else
		${TEST_EXECUTABLE} ${ARGUMENTS[*]} ${OPTIONS[*]} ${INPUT_FILE} 2> /dev/null;
		RESULT=$?;
	fi

	rm -rf ${TMPDIR};

	if test -z "${OPTION_SET}";
	then
		echo -n "Testing ${TEST_DESCRIPTION} with input: ${INPUT_FILE}";
	else
		echo -n "Testing ${TEST_DESCRIPTION} with option: ${OPTION_SET} and input: ${INPUT_FILE}";
	fi

	if test ${RESULT} -ne ${EXIT_SUCCESS};
	then
		echo " (FAIL)";
	else
		echo " (PASS)";
	fi
	return ${RESULT};
}

# Runs the test on the input directory.
#
# Globals:
#   CHECK_WITH_GDB
#   CHECK_WITH_REFERENCE_FILE
#   CHECK_WITH_VALGRIND
#
# Arguments:
#   a string containing the name of the test profile
#   a string containing the description of the test
#   a string containing the name of the option set
#   a string containing the path of the test executable
#   a string containing the path of the test input directory
#   a string containing the input glob
#   an array containing the arguments for the test executable
#
# Returns:
#   an integer containg the exit status of the test executable
#
run_test_on_input_directory()
{
	local TEST_PROFILE=$1;
	local TEST_DESCRIPTION=$2;
	local OPTION_SETS=$3;
	local TEST_EXECUTABLE=$4;
	local TEST_INPUT_DIRECTORY=$5;
	local INPUT_GLOB=$6;
	shift 6;
	local ARGUMENTS=$@;

	check_availability_binary cat;
	check_availability_binary diff;
	check_availability_binary file;
	check_availability_binary gzip;
	check_availability_binary ls;
	check_availability_binary readlink;
	check_availability_binary sed;
	check_availability_binary tr;
	check_availability_binary wc;
	check_availability_binary zcat;

	if ! test -z ${CHECK_WITH_GDB};
	then
		check_availability_binary gdb;

	elif ! test -z ${CHECK_WITH_VALGRIND};
	then
		check_availability_binary valgrind;
	fi

	if ! test -x ${TEST_EXECUTABLE};
	then
		echo "Invalid test executable: ${TEST_EXECUTABLE}";
		echo "";

		return ${EXIT_FAILURE};
	fi

	if ! test -d "${TEST_INPUT_DIRECTORY}";
	then
		echo "Test input directory: ${TEST_INPUT_DIRECTORY} not found.";

		return ${EXIT_IGNORE};
	fi
	local RESULT=`ls ${TEST_INPUT_DIRECTORY}/* | tr ' ' '\n' | wc -l`;

	if test ${RESULT} -eq 0;
	then
		echo "No files or directories found in the test input directory: ${TEST_INPUT_DIRECTORY}";

		return ${EXIT_IGNORE};
	fi

	local TEST_PROFILE_DIRECTORY=$(get_test_profile_directory "${TEST_INPUT_DIRECTORY}" "${TEST_PROFILE}");

	local IGNORE_LIST=$(read_ignore_list "${TEST_PROFILE_DIRECTORY}");

	for TEST_SET_INPUT_DIRECTORY in ${TEST_INPUT_DIRECTORY}/*;
	do
		if ! test -d "${TEST_SET_INPUT_DIRECTORY}";
		then
			continue;
		fi
		if check_for_directory_in_ignore_list "${TEST_SET_INPUT_DIRECTORY}" "${IGNORE_LIST}";
		then
			continue;
		fi

		local TEST_SET_DIRECTORY=$(get_test_set_directory "${TEST_PROFILE_DIRECTORY}" "${TEST_SET_INPUT_DIRECTORY}");

		local INPUT_FILES=$(get_test_input_files "${TEST_SET_INPUT_DIRECTORY}" "${TEST_SET_DIRECTORY}" "${INPUT_GLOB}");

		for INPUT_FILE in ${INPUT_FILES};
		do
			local TESTED_WITH_OPTIONS=0;

			for OPTION_SET in `echo ${OPTION_SETS} | tr ' ' '\n'`;
			do
				local OPTION_FILE=$(get_testion_option_file "${TEST_SET_DIRECTORY}" "${INPUT_FILE}" "${OPTION_SET}");

				if ! test -f ${OPTION_FILE};
				then
					continue
				fi

				if ! run_test_on_input_file "${TEST_SET_DIRECTORY}" "${TEST_DESCRIPTION}" "${OPTION_SET}" "${TEST_EXECUTABLE}" "${INPUT_FILE}" ${ARGUMENTS[*]};
				then
					return ${EXIT_FAILURE};
				fi
				TESTED_WITH_OPTIONS=1;
			done

			if test ${TESTED_WITH_OPTIONS} -eq 0;
			then
				if ! run_test_on_input_file "${TEST_SET_DIRECTORY}" "${TEST_DESCRIPTION}" "" "${TEST_EXECUTABLE}" "${INPUT_FILE}" ${ARGUMENTS[*]};
				then
					return ${EXIT_FAILURE};
				fi
			fi
		done
	done

	return ${EXIT_SUCCESS};
}

