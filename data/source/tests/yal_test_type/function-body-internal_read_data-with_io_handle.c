	/* Test regular cases
	 */
	result = ${library_name}_internal_${type_name}_read_data(
	          (${library_name}_internal_${type_name}_t *) ${type_name},
	          io_handle,
	          ${library_name_suffix}_test_${type_name}_data1,
	          ${test_data_size},
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
	result = ${library_name}_internal_${type_name}_read_data(
	          NULL,
	          io_handle,
	          ${library_name_suffix}_test_${type_name}_data1,
	          ${test_data_size},
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

	result = ${library_name}_internal_${type_name}_read_data(
	          (${library_name}_internal_${type_name}_t *) ${type_name},
	          NULL,
	          ${library_name_suffix}_test_${type_name}_data1,
	          ${test_data_size},
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

	result = ${library_name}_internal_${type_name}_read_data(
	          (${library_name}_internal_${type_name}_t *) ${type_name},
	          io_handle,
	          NULL,
	          ${test_data_size},
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

	result = ${library_name}_internal_${type_name}_read_data(
	          (${library_name}_internal_${type_name}_t *) ${type_name},
	          io_handle,
	          ${library_name_suffix}_test_${type_name}_data1,
	          (size_t) SSIZE_MAX + 1,
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

	result = ${library_name}_internal_${type_name}_read_data(
	          (${library_name}_internal_${type_name}_t *) ${type_name},
	          io_handle,
	          ${library_name_suffix}_test_${type_name}_data1,
	          0,
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

