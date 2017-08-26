/* Tests the ${library_name}_${type_name}_compare function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_compare(
     void )
{
	libcerror_error_t *error                            = NULL;
	${library_name}_${type_name}_t *first_${type_name}  = NULL;
	${library_name}_${type_name}_t *second_${type_name} = NULL;
	int result                                          = 0;

	/* Initialize test
	 */
	result = ${library_name}_${type_name}_initialize(
	          &first_${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "first_${type_name}",
	 first_${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = ${library_name}_${type_name}_initialize(
	          &second_${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "second_${type_name}",
	 second_${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test regular cases
	 */
	result = ${library_name}_${type_name}_compare(
	          first_${type_name},
	          second_${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 LIBCDATA_COMPARE_EQUAL );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test error cases
	 */
	result = ${library_name}_${type_name}_compare(
	          NULL,
	          second_${type_name},
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

	result = ${library_name}_${type_name}_compare(
	          first_${type_name},
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

	/* Clean up
	 */
	result = ${library_name}_${type_name}_free(
	          &second_${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "second_${type_name}",
	 second_${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = ${library_name}_${type_name}_free(
	          &first_${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "first_${type_name}",
	 first_${type_name} );

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
	if( second_${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 &second_${type_name},
		 NULL );
	}
	if( first_${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 &first_${type_name},
		 NULL );
	}
	return( 0 );
}

