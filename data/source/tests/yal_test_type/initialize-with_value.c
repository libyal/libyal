/* Tests the ${library_name}_${type_name}_initialize function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_initialize(
     void )
{
	libcerror_error_t *error                       = NULL;
	${library_name}_${type_name}_t *${type_name}   = NULL;
	${library_name}_${value_type}_t *${value_name} = NULL;
	int result                                     = 0;

#if defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY )
	int number_of_malloc_fail_tests                = 1;
	int number_of_memset_fail_tests                = 1;
	int test_number                                = 0;
#endif

	/* Initialize test
	 */
	result = ${library_name}_${value_type}_initialize(
	          &${value_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "${value_name}",
	 ${value_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test regular cases
	 */
	result = ${library_name}_${type_name}_initialize(
	          &${type_name},
	          ${value_name},
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

	/* Test error cases
	 */
	result = ${library_name}_${type_name}_initialize(
	          NULL,
	          ${value_name},
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

	${type_name} = (${library_name}_${type_name}_t *) 0x12345678UL;

	result = ${library_name}_${type_name}_initialize(
	          &${type_name},
	          ${value_name},
	          &error );

	${type_name} = NULL;

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	result = ${library_name}_${type_name}_initialize(
	          &${type_name},
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

#if defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY )

	for( test_number = 0;
	     test_number < number_of_malloc_fail_tests;
	     test_number++ )
	{
		/* Test ${library_name}_${type_name}_initialize with malloc failing
		 */
		${library_name_suffix}_test_malloc_attempts_before_fail = test_number;

		result = ${library_name}_${type_name}_initialize(
		          &${type_name},
		          ${value_name},
		          &error );

		if( ${library_name_suffix}_test_malloc_attempts_before_fail != -1 )
		{
			${library_name_suffix}_test_malloc_attempts_before_fail = -1;

			if( ${type_name} != NULL )
			{
				${library_name}_${type_name}_free(
				 &${type_name},
				 NULL );
			}
		}
		else
		{
			${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
			 "result",
			 result,
			 -1 );

			${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
			 "${type_name}",
			 ${type_name} );

			${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
			 "error",
			 error );

			libcerror_error_free(
			 &error );
		}
	}
	for( test_number = 0;
	     test_number < number_of_memset_fail_tests;
	     test_number++ )
	{
		/* Test ${library_name}_${type_name}_initialize with memset failing
		 */
		${library_name_suffix}_test_memset_attempts_before_fail = test_number;

		result = ${library_name}_${type_name}_initialize(
		          &${type_name},
		          ${value_name},
		          &error );

		if( ${library_name_suffix}_test_memset_attempts_before_fail != -1 )
		{
			${library_name_suffix}_test_memset_attempts_before_fail = -1;

			if( ${type_name} != NULL )
			{
				${library_name}_${type_name}_free(
				 &${type_name},
				 NULL );
			}
		}
		else
		{
			${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
			 "result",
			 result,
			 -1 );

			${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
			 "${type_name}",
			 ${type_name} );

			${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
			 "error",
			 error );

			libcerror_error_free(
			 &error );
		}
	}
#endif /* defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY ) */

	/* Clean up
	 */
	result = ${library_name}_${value_type}_free(
	          &${value_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "${value_name}",
	 ${value_name} );

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
	if( ${value_name} != NULL )
	{
		${library_name}_${value_type}_free(
		 &${value_name},
		 NULL );
	}
	return( 0 );
}

