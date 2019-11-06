/* Tests the ${library_name}_${type_name}_read_buffer function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_read_buffer(
     ${library_name}_${type_name}_t *${type_name} )
{
	uint8_t buffer[ ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_READ_BUFFER_SIZE ];

	libcerror_error_t *error             = NULL;
	time_t timestamp                     = 0;
	size64_t ${type_size_name}           = 0;
	size64_t remaining_${type_size_name} = 0;
	size_t read_size                     = 0;
	ssize_t read_count                   = 0;
	off64_t offset                       = 0;
	int number_of_tests                  = 1024;
	int random_number                    = 0;
	int result                           = 0;
	int test_number                      = 0;

#if defined( ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_VERBOSE )
	off64_t media_offset                 = 0;
#endif

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
	read_size = ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_READ_BUFFER_SIZE;

	if( ${type_size_name} < ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_READ_BUFFER_SIZE )
	{
		read_size = (size_t) ${type_size_name};
	}
	read_count = ${library_name}_${type_name}_read_buffer(
	              ${type_name},
	              buffer,
	              ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_READ_BUFFER_SIZE,
	              &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
	 "read_count",
	 read_count,
	 (ssize_t) read_size );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	if( ${type_size_name} > 8 )
	{
		/* Set offset to ${type_size_name} - 8
		 */
		offset = ${library_name}_${type_name}_seek_offset(
		          ${type_name},
		          -8,
		          SEEK_END,
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT64(
		 "offset",
		 offset,
		 (int64_t) ${type_size_name} - 8 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		/* Read buffer on ${type_size_name} boundary
		 */
		read_count = ${library_name}_${type_name}_read_buffer(
		              ${type_name},
		              buffer,
		              ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_READ_BUFFER_SIZE,
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
		read_count = ${library_name}_${type_name}_read_buffer(
		              ${type_name},
		              buffer,
		              ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_READ_BUFFER_SIZE,
		              &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) 0 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

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
	}
	/* Stress test read buffer
	 */
	timestamp = time(
	             NULL );

	srand(
	 (unsigned int) timestamp );

	remaining_${type_size_name} = ${type_size_name};

	for( test_number = 0;
	     test_number < number_of_tests;
	     test_number++ )
	{
		random_number = rand();

		${library_name_suffix_upper_case}_TEST_ASSERT_GREATER_THAN_INT(
		 "random_number",
		 random_number,
		 -1 );

		read_size = (size_t) random_number % ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_READ_BUFFER_SIZE;

#if defined( ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_VERBOSE )
		fprintf(
		 stdout,
		 "${library_name}_${type_name}_read_buffer: at offset: %" PRIi64 " (0x%08" PRIx64 ") of size: %" PRIzd "\n",
		 media_offset,
		 media_offset,
		 read_size );
#endif
		read_count = ${library_name}_${type_name}_read_buffer(
		              ${type_name},
		              buffer,
		              read_size,
		              &error );

		if( read_size > remaining_${type_size_name} )
		{
			read_size = (size_t) remaining_${type_size_name};
		}
		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) read_size );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		remaining_${type_size_name} -= read_count;

#if defined( ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_VERBOSE )
		media_offset += read_count;
#endif

		if( remaining_${type_size_name} == 0 )
		{
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

			remaining_${type_size_name} = ${type_size_name};

#if defined( ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_VERBOSE )
			media_offset = 0;
#endif
		}
	}
	/* Test error cases
	 */
	read_count = ${library_name}_${type_name}_read_buffer(
	              NULL,
	              buffer,
	              ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_READ_BUFFER_SIZE,
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
	              ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_READ_BUFFER_SIZE,
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

