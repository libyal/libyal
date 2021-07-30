/* Tests the ${library_name}_${structure_name}_initialize function
 * Returns 1 if successful or 0 if not
 */
int ${prefix}_test_${structure_name}_initialize(
     void )
{
	libcerror_error_t *error          = NULL;
	${library_name}_${structure_name}_t *${structure_name} = NULL;
	int result                        = 0;

#if defined( HAVE_${prefix_upper_case}_TEST_MEMORY )
	int number_of_malloc_fail_tests   = 1;
	int number_of_memset_fail_tests   = 1;
	int test_number                   = 0;
#endif

	/* Test regular cases
	 */
	result = ${library_name}_${structure_name}_initialize(
	          &${structure_name},
	          &error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "${structure_name}",
	 ${structure_name} );

	${prefix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = ${library_name}_${structure_name}_free(
	          &${structure_name},
	          &error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NULL(
	 "${structure_name}",
	 ${structure_name} );

	${prefix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test error cases
	 */
	result = ${library_name}_${structure_name}_initialize(
	          NULL,
	          &error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	${structure_name} = (${library_name}_${structure_name}_t *) 0x12345678UL;

	result = ${library_name}_${structure_name}_initialize(
	          &${structure_name},
	          &error );

	${structure_name} = NULL;

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

#if defined( HAVE_${prefix_upper_case}_TEST_MEMORY )

	for( test_number = 0;
	     test_number < number_of_malloc_fail_tests;
	     test_number++ )
	{
		/* Test ${library_name}_${structure_name}_initialize with malloc failing
		 */
		${prefix}_test_malloc_attempts_before_fail = test_number;

		result = ${library_name}_${structure_name}_initialize(
		          &${structure_name},
		          &error );

		if( ${prefix}_test_malloc_attempts_before_fail != -1 )
		{
			${prefix}_test_malloc_attempts_before_fail = -1;

			if( ${structure_name} != NULL )
			{
				${library_name}_${structure_name}_free(
				 &${structure_name},
				 NULL );
			}
		}
		else
		{
			${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
			 "result",
			 result,
			 -1 );

			${prefix_upper_case}_TEST_ASSERT_IS_NULL(
			 "${structure_name}",
			 ${structure_name} );

			${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
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
		/* Test ${library_name}_${structure_name}_initialize with memset failing
		 */
		${prefix}_test_memset_attempts_before_fail = test_number;

		result = ${library_name}_${structure_name}_initialize(
		          &${structure_name},
		          &error );

		if( ${prefix}_test_memset_attempts_before_fail != -1 )
		{
			${prefix}_test_memset_attempts_before_fail = -1;

			if( ${structure_name} != NULL )
			{
				${library_name}_${structure_name}_free(
				 &${structure_name},
				 NULL );
			}
		}
		else
		{
			${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
			 "result",
			 result,
			 -1 );

			${prefix_upper_case}_TEST_ASSERT_IS_NULL(
			 "${structure_name}",
			 ${structure_name} );

			${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
			 "error",
			 error );

			libcerror_error_free(
			 &error );
		}
	}
#endif /* defined( HAVE_${prefix_upper_case}_TEST_MEMORY ) */

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	if( ${structure_name} != NULL )
	{
		${library_name}_${structure_name}_free(
		 &${structure_name},
		 NULL );
	}
	return( 0 );
}

