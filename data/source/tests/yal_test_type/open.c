/* Tests the ${library_name}_${library_type}_open functions
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${library_type}_open(
     const system_character_t *source )
{
	char narrow_source[ 256 ];

	libcerror_error_t *error = NULL;
	${library_name}_${library_type}_t *${library_type}      = NULL;
	int result               = 0;

	/* Initialize test
	 */
	result = ${library_name_suffix}_test_${library_type}_get_narrow_source(
	          source,
	          narrow_source,
	          256,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "error",
         error );

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

	/* Test open
	 */
	result = ${library_name}_${library_type}_open(
	          ${library_type},
	          narrow_source,
	          ${library_name_upper_case}_OPEN_READ,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "error",
         error );

	/* Clean up
	 */
	result = ${library_name}_${library_type}_close(
	          ${library_type},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 0 );

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

#if defined( HAVE_WIDE_CHARACTER_TYPE )

/* Tests the ${library_name}_${library_type}_open_wide functions
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${library_type}_open_wide(
     const system_character_t *source )
{
	wchar_t wide_source[ 256 ];

	libcerror_error_t *error = NULL;
	${library_name}_${library_type}_t *${library_type}      = NULL;
	int result               = 0;

	/* Initialize test
	 */
	result = ${library_name_suffix}_test_${library_type}_get_wide_source(
	          source,
	          wide_source,
	          256,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "error",
         error );

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

	/* Test open
	 */
	result = ${library_name}_${library_type}_open_wide(
	          ${library_type},
	          wide_source,
	          ${library_name_upper_case}_OPEN_READ,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "error",
         error );

	/* Clean up
	 */
	result = ${library_name}_${library_type}_close(
	          ${library_type},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 0 );

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

#endif /* defined( HAVE_WIDE_CHARACTER_TYPE ) */

