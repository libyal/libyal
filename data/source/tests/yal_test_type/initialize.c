/* Tests the ${library_name}_${library_type}_initialize function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${library_type}_initialize(
     void )
{
	libcerror_error_t *error = NULL;
	${library_name}_${library_type}_t *${library_type}      = NULL;
	int result               = 0;

	/* Test ${library_type} initialization
	 */
	result = ${library_name}_${library_type}_initialize(
	          &${library_type},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
         "${library_type}",
         ${library_type} );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "error",
         error );

	result = ${library_name}_${library_type}_free(
	          &${library_type},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "${library_type}",
         ${library_type} );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "error",
         error );

	/* Test error cases
	 */
	result = ${library_name}_${library_type}_initialize(
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

	${library_type} = (${library_name}_${library_type}_t *) 0x12345678UL;

	result = ${library_name}_${library_type}_initialize(
	          &${library_type},
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

	${library_type} = NULL;

#if defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY )

	/* Test ${library_name}_${library_type}_initialize with malloc failing
	 */
	${library_name_suffix}_test_malloc_attempts_before_fail = 0;

	result = ${library_name}_${library_type}_initialize(
	          &${library_type},
	          &error );

	if( ${library_name_suffix}_test_malloc_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_malloc_attempts_before_fail = -1;

		if( ${library_type} != NULL )
		{
			${library_name}_${library_type}_free(
			 &${library_type},
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
		 "${library_type}",
		 ${library_type} );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
	/* Test ${library_name}_${library_type}_initialize with memset failing
	 */
	${library_name_suffix}_test_memset_attempts_before_fail = 0;

	result = ${library_name}_${library_type}_initialize(
	          &${library_type},
	          &error );

	if( ${library_name_suffix}_test_memset_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_memset_attempts_before_fail = -1;

		if( ${library_type} != NULL )
		{
			${library_name}_${library_type}_free(
			 &${library_type},
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
		 "${library_type}",
		 ${library_type} );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
#endif /* defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY ) */

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	if( ${library_type} != NULL )
	{
		${library_name}_${library_type}_free(
		 &${library_type},
		 NULL );
	}
	return( 0 );
}

