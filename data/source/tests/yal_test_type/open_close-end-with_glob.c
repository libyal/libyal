	/* Test open and close
	 */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_${type_name}_open_wide(
	          ${type_name},
	          (wchar_t * const *) filenames,
	          number_of_filenames,
	          ${library_name:upper_case}_OPEN_READ,
	          &error );
#else
	result = ${library_name}_${type_name}_open(
	          ${type_name},
	          (char * const *) filenames,
	          number_of_filenames,
	          ${library_name:upper_case}_OPEN_READ,
	          &error );
#endif

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = ${library_name}_${type_name}_close(
	          ${type_name},
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 0 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test open and close a second time to validate clean up on close
	 */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_${type_name}_open_wide(
	          ${type_name},
	          (wchar_t * const *) filenames,
	          number_of_filenames,
	          ${library_name:upper_case}_OPEN_READ,
	          &error );
#else
	result = ${library_name}_${type_name}_open(
	          ${type_name},
	          (char * const *) filenames,
	          number_of_filenames,
	          ${library_name:upper_case}_OPEN_READ,
	          &error );
#endif

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = ${library_name}_${type_name}_close(
	          ${type_name},
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 0 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Clean up
	 */
	result = ${library_name}_${type_name}_free(
	          &${type_name},
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "${type_name}",
	 ${type_name} );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_glob_wide_free(
	          filenames,
	          number_of_filenames,
	          &error );
#else
	result = ${library_name}_glob_free(
	          filenames,
	          number_of_filenames,
	          &error );
#endif
	filenames = NULL;

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
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
	if( filenames != NULL )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		${library_name}_glob_wide_free(
		 filenames,
		 number_of_filenames,
		 NULL );
#else
		${library_name}_glob_free(
		 filenames,
		 number_of_filenames,
		 NULL );
#endif
	}
	return( 0 );
}

