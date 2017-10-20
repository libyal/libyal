/* Tests the ${library_name}_${type_name}_read_buffer_at_offset function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_read_buffer_at_offset(
     ${library_name}_${type_name}_t *${type_name} )
{
	uint8_t buffer[ 16 ];

	libcerror_error_t *error = NULL;
	size64_t size            = 0;
	ssize_t read_count       = 0;
	off64_t offset           = 0;

	/* Determine size
	 */
	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          0,
	          SEEK_END,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_NOT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	size = (size64_t) offset;

	/* Test regular cases
	 */
	if( size > 16 )
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

		/* Read buffer on size boundary
		 */
		read_count = ${library_name}_${type_name}_read_buffer_at_offset(
		              ${type_name},
		              buffer,
		              16,
		              size - 8,
		              &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) 8 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		/* Read buffer beyond size boundary
		 */
		read_count = ${library_name}_${type_name}_read_buffer(
		              ${type_name},
		              buffer,
		              16,
		              size + 8,
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

