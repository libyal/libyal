/* Tests the ${library_name}_${type_name}_clone function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_clone(
     void )
{
	libcerror_error_t *error                                 = NULL;
	${library_name}_${type_name}_t *destination_${type_name} = NULL;
	${library_name}_${type_name}_t *source_${type_name}      = NULL;
	int result                                               = 0;

	/* Initialize test
	 */
	result = ${library_name}_${type_name}_initialize(
	          &source_${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
         "source_${type_name}",
         source_${type_name} );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "error",
         error );

	/* Test regular cases
	 */
	result = ${library_name}_${type_name}_clone(
	          &destination_${type_name},
	          source_${type_name},
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

	result = ${library_name}_${type_name}_free(
	          &destination_${type_name},
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

	result = ${library_name}_${type_name}_clone(
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

	/* Test error cases
	 */
	result = ${library_name}_${type_name}_clone(
	          NULL,
	          source_${type_name},
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
	          &source_${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "source_${type_name}",
         source_${type_name} );

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
	if( destination_${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 &destination_${type_name},
		 NULL );
	}
	if( source_${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 &source_${type_name},
		 NULL );
	}
	return( 0 );
}

