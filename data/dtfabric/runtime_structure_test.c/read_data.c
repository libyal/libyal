/* Tests the ${library_name}_${structure_name}_read_data function
 * Returns 1 if successful or 0 if not
 */
int ${prefix}_test_${structure_name}_read_data(
     void )
{
	libcerror_error_t *error          = NULL;
	${library_name}_${structure_name}_t *${structure_name} = NULL;
	int result                        = 0;

	/* Initialize test
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

	/* Test regular cases
	 */
	result = ${library_name}_${structure_name}_read_data(
	          ${structure_name},
	          ${prefix}_test_${structure_name}_data1,
	          76,
	          &error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_UINT32(
	 "${structure_name}->file_size",
	 ${structure_name}->file_size,
	 709904 );

	/* Test error cases
	 */
	result = ${library_name}_${structure_name}_read_data(
	          NULL,
	          ${prefix}_test_${structure_name}_data1,
	          76,
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

	result = ${library_name}_${structure_name}_read_data(
	          ${structure_name},
	          NULL,
	          76,
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

	result = ${library_name}_${structure_name}_read_data(
	          ${structure_name},
	          ${prefix}_test_${structure_name}_data1,
	          0,
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

	result = ${library_name}_${structure_name}_read_data(
	          ${structure_name},
	          ${prefix}_test_${structure_name}_data1,
	          (size_t) SSIZE_MAX + 1,
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

#if defined( HAVE_${prefix_upper_case}_TEST_MEMORY )

	/* Test ${prefix}_test_${structure_name}_read_data with memcpy failing
	 */
	${prefix}_test_memcpy_attempts_before_fail = 0;

	result = ${library_name}_${structure_name}_read_data(
	          ${structure_name},
	          ${prefix}_test_${structure_name}_data1,
	          76,
	          &error );

	if( ${prefix}_test_memcpy_attempts_before_fail != -1 )
	{
		${prefix}_test_memcpy_attempts_before_fail = -1;
	}
	else
	{
		${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 -1 );

		${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
#endif /* defined( HAVE_${prefix_upper_case}_TEST_MEMORY ) */

	/* Test error case where header size is invalid
	 */
	byte_stream_copy_from_uint32_little_endian(
	 ${prefix}_test_${structure_name}_data1,
	 0xffffffffUL );

	result = ${library_name}_${structure_name}_read_data(
	          ${structure_name},
	          ${prefix}_test_${structure_name}_data1,
	          76,
	          &error );

	byte_stream_copy_from_uint32_little_endian(
	 ${prefix}_test_${structure_name}_data1,
	 0x0000004cUL );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	/* Test error case where class identifier is invalid
	 */
	byte_stream_copy_from_uint32_little_endian(
	 &( ${prefix}_test_${structure_name}_data1[ 4 ] ),
	 0xffffffffUL );

	result = ${library_name}_${structure_name}_read_data(
	          ${structure_name},
	          ${prefix}_test_${structure_name}_data1,
	          76,
	          &error );

	byte_stream_copy_from_uint32_little_endian(
	 &( ${prefix}_test_${structure_name}_data1[ 4 ] ),
	 0x00021401UL );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	/* Clean up
	 */
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

