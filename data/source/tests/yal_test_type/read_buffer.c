/* Tests the ${library_name}_${type_name}_read_buffer function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_read_buffer(
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

	/* Reset offset to 0
	 */
	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          0,
	          SEEK_SET,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) 0 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test regular cases
	 */
	if( size > 16 )
	{
		read_count = ${library_name}_${type_name}_read_buffer(
		              ${type_name},
		              buffer,
		              16,
		              &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) 16 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );
	}
/* TODO read on size boundary */
/* TODO read beyond size boundary */

	/* Reset offset to 0
	 */
	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          0,
	          SEEK_SET,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) 0 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test error cases
	 */
	read_count = ${library_name}_${type_name}_read_buffer(
	              NULL,
	              buffer,
	              16,
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

	read_count = ${library_name}_${type_name}_read_buffer(
	              ${type_name},
	              NULL,
	              16,
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

	read_count = ${library_name}_${type_name}_read_buffer(
	              ${type_name},
	              buffer,
	              (size_t) SSIZE_MAX + 1,
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

