
mkdir -p "$${TESTS_INPUT_DIRECTORY}/$${TEST_SET}"

for TEST_FILE in $${TEST_FILES}
do
	URL="https://raw.githubusercontent.com/${test_data_repository}/refs/heads/main/${test_data_path}/$${TEST_FILE}"

	curl -L -o "$${TESTS_INPUT_DIRECTORY}/$${TEST_SET}/$${TEST_FILE}" $${URL}
done
