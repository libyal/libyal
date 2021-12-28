/* Tests the ${library_name}_${structure_name}_read_file_io_handle function
 * Returns 1 if successful or 0 if not
 */
int ${prefix}_test_${structure_name}_read_file_io_handle(
     void )
{
	libbfio_handle_t *file_io_handle  = NULL;
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

	/* Initialize file IO handle
	 */
	result = ${prefix}_test_open_file_io_handle(
	          &file_io_handle,
	          ${prefix}_test_${structure_name}_data1,
	          ${test_data_size},
	          &error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "file_io_handle",
	 file_io_handle );

	${prefix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test regular cases
	 */
	result = ${library_name}_${structure_name}_read_file_io_handle(
	          ${structure_name},
	          file_io_handle,
	          0,
	          &error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test error cases
	 */
	result = ${library_name}_${structure_name}_read_file_io_handle(
	          NULL,
	          file_io_handle,
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

	result = ${library_name}_${structure_name}_read_file_io_handle(
	          ${structure_name},
	          NULL,
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

	/* Clean up file IO handle
	 */
	result = ${prefix}_test_close_file_io_handle(
	          &file_io_handle,
	          &error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 0 );

	${prefix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test data too small
	 */
	result = ${prefix}_test_open_file_io_handle(
	          &file_io_handle,
	          ${prefix}_test_${structure_name}_data1,
	          ${test_data_size} - 1,
	          &error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "file_io_handle",
	 file_io_handle );

	${prefix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = ${library_name}_${structure_name}_read_file_io_handle(
	          ${structure_name},
	          file_io_handle,
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

	result = ${prefix}_test_close_file_io_handle(
	          &file_io_handle,
	          &error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 0 );

	${prefix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

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
	if( file_io_handle != NULL )
	{
		libbfio_handle_free(
		 &file_io_handle,
		 NULL );
	}
	if( ${structure_name} != NULL )
	{
		${library_name}_${structure_name}_free(
		 &${structure_name},
		 NULL );
	}
	return( 0 );
}

