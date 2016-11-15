/* Tests the ${library_name}_${type_name}_get_${value_name} function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_get_${value_name}(
     ${library_name}_${type_name}_t *${type_name} )
{
	libcerror_error_t *error     = NULL;
	${value_type} *${value_name} = 0;
	int ${value_name}_is_set     = 0;
	int result                   = 0;

	/* Test regular cases
	 */
	result = ${library_name}_${type_name}_get_${value_name}(
	          ${type_name},
	          &${value_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_NOT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	${value_name}_is_set = result;

	if( ${value_name}_is_set != 0 )
	{
		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "${value_name}",
		 ${value_name} );

		result = ${library_name}_${value_type}_free(
		          &${value_name},
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );
	}
	/* Test error cases
	 */
	result = ${library_name}_${type_name}_get_${value_name}(
	          NULL,
	          &${value_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "${value_name}",
	 ${value_name} );

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
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 -1 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "${value_name}",
		 ${value_name} );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	if( ${value_name} != NULL )
	{
		${library_name}_${value_type}_free(
		 &${value_name},
		 NULL );
	}
	return( 0 );
}

