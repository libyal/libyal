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

	destination_${type_name} = (${library_name}_${type_name}_t *) 0x12345678UL;

	result = ${library_name}_${type_name}_clone(
	          &destination_${type_name},
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

	destination_${type_name} = NULL;

#if defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY )

	/* Test ${library_name}_${type_name}_clone with malloc failing
	 */
	${library_name_suffix}_test_malloc_attempts_before_fail = 0;

	result = ${library_name}_${type_name}_clone(
	          &destination_${type_name},
	          source_${type_name},
	          &error );

	if( ${library_name_suffix}_test_malloc_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_malloc_attempts_before_fail = -1;

		if( destination_${type_name} != NULL )
		{
			${library_name}_${type_name}_free(
			 &destination_${type_name},
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
		 "destination_${type_name}",
		 destination_${type_name} );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}

	/* Test ${library_name}_${type_name}_clone with memcpy failing
	 */
	${library_name_suffix}_test_memcpy_attempts_before_fail = 0;

	result = ${library_name}_${type_name}_clone(
	          &destination_${type_name},
	          source_${type_name},
	          &error );

	if( ${library_name_suffix}_test_memcpy_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_memcpy_attempts_before_fail = -1;

		if( destination_${type_name} != NULL )
		{
			${library_name}_${type_name}_free(
			 &destination_${type_name},
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
		 "destination_${type_name}",
		 destination_${type_name} );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
#endif /* defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY ) */

