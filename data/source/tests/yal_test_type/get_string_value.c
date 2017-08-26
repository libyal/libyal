/* Tests the ${library_name}_${type_name}_get_${value_name} function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_get_${value_name}(
     void )
{
	${value_type} ${value_name}[ 512 ];

	libcerror_error_t *error                     = NULL;
	${library_name}_${type_name}_t *${type_name} = NULL;
	int ${value_name}_is_set                     = 0;
	int result                                   = 0;

	/* Initialize test
	 */
	result = ${library_name}_${type_name}_initialize(
	          &${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "${type_name}",
	 ${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test regular cases
	 */
	result = ${library_name}_${type_name}_get_${value_name}(
	          ${type_name},
	          ${value_name},
	          512,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_NOT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	${value_name}_is_set = result;

	/* Test error cases
	 */
	result = ${library_name}_${type_name}_get_${value_name}(
	          NULL,
	          ${value_name},
	          512,
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

	if( ${value_name}_is_set != 0 )
	{
		result = ${library_name}_${type_name}_get_${value_name}(
		          ${type_name},
		          NULL,
		          512,
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

		result = ${library_name}_${type_name}_get_${value_name}(
		          ${type_name},
		          ${value_name},
		          0,
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

		result = ${library_name}_${type_name}_get_${value_name}(
		          ${type_name},
		          ${value_name},
		          (size_t) SSIZE_MAX + 1,
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
	}
	/* Clean up
	 */
	result = ${library_name}_${type_name}_free(
	          &${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "${type_name}",
	 ${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	if( ${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 &${type_name},
		 NULL );
	}
	return( 0 );
}

