/* Tests the ${library_name}_${type_name}_read_buffer_at_offset function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_read_buffer_at_offset(
     ${library_name}_${type_name}_t *${type_name} )
{
	uint8_t buffer[ 16 ];

	libcerror_error_t *error   = NULL;
	size64_t ${type_size_name} = 0;
	ssize_t read_count         = 0;
	int result                 = 0;

	/* Determine size
	 */
	result = ${library_name}_${type_name}_get_${type_size_name}(
	          ${type_name},
	          &${type_size_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test regular cases
	 */
	if( ${type_size_name} > 16 )
	{
		read_count = ${library_name}_${type_name}_read_buffer_at_offset(
		              ${type_name},
		              buffer,
		              16,
		              0,
		              &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) 16 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		/* Read buffer on ${type_size_name} boundary
		 */
		read_count = ${library_name}_${type_name}_read_buffer_at_offset(
		              ${type_name},
		              buffer,
		              16,
		              ${type_size_name} - 8,
		              &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) 8 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		/* Read buffer beyond ${type_size_name} boundary
		 */
		read_count = ${library_name}_${type_name}_read_buffer_at_offset(
		              ${type_name},
		              buffer,
		              16,
		              ${type_size_name} + 8,
		              &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) 0 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );
	}
	/* Test error cases
	 */
	read_count = ${library_name}_${type_name}_read_buffer_at_offset(
	              NULL,
	              buffer,
	              16,
	              0,
	              &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
	 "read_count",
	 read_count,
	 (ssize_t) -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	read_count = ${library_name}_${type_name}_read_buffer_at_offset(
	              ${type_name},
	              NULL,
	              16,
	              0,
	              &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
	 "read_count",
	 read_count,
	 (ssize_t) -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	read_count = ${library_name}_${type_name}_read_buffer_at_offset(
	              ${type_name},
	              buffer,
	              (size_t) SSIZE_MAX + 1,
	              0,
	              &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
	 "read_count",
	 read_count,
	 (ssize_t) -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	read_count = ${library_name}_${type_name}_read_buffer_at_offset(
	              ${type_name},
	              buffer,
	              16,
	              -1,
	              &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
	 "read_count",
	 read_count,
	 (ssize_t) -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	return( 0 );
}

