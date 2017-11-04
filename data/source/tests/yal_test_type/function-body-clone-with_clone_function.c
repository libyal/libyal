	/* Test lib${library_name_suffix}_${type_name}_clone on initialized ${type_name}
	 */
	result = lib${library_name_suffix}_${type_name}_clone(
	          &destination_${type_name},
	          source_${type_name},
	          &${library_name_suffix}_test_${type_name}_${value_name}_free_function,
	          &${library_name_suffix}_test_${type_name}_${value_name}_clone_function,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "destination_${type_name}",
	 destination_${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = lib${library_name_suffix}_${type_name}_free(
	          &destination_${type_name},
	          NULL,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "destination_${type_name}",
	 destination_${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test lib${library_name_suffix}_${type_name}_clone on non-initialized ${type_name}
	 */
	result = lib${library_name_suffix}_${type_name}_clone(
	          &destination_${type_name},
	          NULL,
	          &${library_name_suffix}_test_${type_name}_${value_name}_free_function,
	          &${library_name_suffix}_test_${type_name}_${value_name}_clone_function,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "destination_${type_name}",
	 destination_${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test error cases
	 */
	result = lib${library_name_suffix}_${type_name}_clone(
	          NULL,
	          NULL,
	          NULL,
	          NULL,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "destination_${type_name}",
	 destination_${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	destination_${type_name} = (lib${library_name_suffix}_${type_name}_t *) 0x12345678UL;

	result = lib${library_name_suffix}_${type_name}_clone(
	          &destination_${type_name},
	          NULL,
	          NULL,
	          NULL,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	destination_${type_name} = NULL;

	result = lib${library_name_suffix}_${type_name}_clone(
	          &destination_${type_name},
	          NULL,
	          NULL,
	          NULL,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

