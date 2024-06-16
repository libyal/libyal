	/* Test regular cases
	 */
	result = ${library_name}_${type_name}_copy_from_byte_stream(
	          ${type_name},
	          ${library_name_suffix}_test_${type_name}_data1,
	          ${test_data_size},
	          ${library_name:upper_case}_CODEPAGE_WINDOWS_1252,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test error cases
	 */
	result = ${library_name}_${type_name}_copy_from_byte_stream(
	          NULL,
	          ${library_name_suffix}_test_${type_name}_data1,
	          ${test_data_size},
	          ${library_name:upper_case}_CODEPAGE_WINDOWS_1252,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	result = ${library_name}_${type_name}_copy_from_byte_stream(
	          ${type_name},
	          NULL,
	          ${test_data_size},
	          ${library_name:upper_case}_CODEPAGE_WINDOWS_1252,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	result = ${library_name}_${type_name}_copy_from_byte_stream(
	          ${type_name},
	          ${library_name_suffix}_test_${type_name}_data1,
	          (size_t) SSIZE_MAX + 1,
	          ${library_name:upper_case}_CODEPAGE_WINDOWS_1252,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	result = ${library_name}_${type_name}_copy_from_byte_stream(
	          ${type_name},
	          ${library_name_suffix}_test_${type_name}_data1,
	          0,
	          ${library_name:upper_case}_CODEPAGE_WINDOWS_1252,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	/* TODO: test with invalid codepage */

