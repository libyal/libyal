	/* Initialize test
	 */
	result = ${library_name}_${type_name}_initialize(
	          &source_${type_name},
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "source_${type_name}",
	 source_${type_name} );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

