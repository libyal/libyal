/* Tests the ${library_name}_${type_name}_read_buffer_at_offset function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_read_buffer_at_offset(
     ${library_name}_${type_name}_t *${type_name} )
{
	uint8_t buffer[ ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE ];

	libcerror_error_t *error             = NULL;
	time_t timestamp                     = 0;
	size64_t ${type_size_name}           = 0;
	size64_t remaining_${type_size_name} = 0;
	size_t read_size                     = 0;
	ssize_t read_count                   = 0;
	off64_t read_offset                  = 0;
	off64_t offset                       = 0;
	int number_of_tests                  = 1024;
	int random_number                    = 0;
	int result                           = 0;
	int test_number                      = 0;

	/* Determine size
	 */
	result = ${library_name}_${type_name}_get_${type_size_name}(
	          ${type_name},
	          &${type_size_name},
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test regular cases
	 */
	read_size = ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE;

	if( ${type_size_name} < ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE )
	{
		read_size = (size_t) ${type_size_name};
	}
	read_count = ${library_name}_${type_name}_read_buffer_at_offset(
	              ${type_name},
	              buffer,
	              ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE,
	              0,
	              &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_SSIZE(
	 "read_count",
	 read_count,
	 (ssize_t) read_size );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	if( ${type_size_name} > 8 )
	{
		/* Read buffer on ${type_size_name} boundary
		 */
		read_count = ${library_name}_${type_name}_read_buffer_at_offset(
		              ${type_name},
		              buffer,
		              ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE,
		              ${type_size_name} - 8,
		              &error );

		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) 8 );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		/* Read buffer beyond ${type_size_name} boundary
		 */
		read_count = ${library_name}_${type_name}_read_buffer_at_offset(
		              ${type_name},
		              buffer,
		              ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE,
		              ${type_size_name} + 8,
		              &error );

		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) 0 );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );
	}
	/* Stress test read buffer
	 */
	timestamp = time(
	             NULL );

	srand(
	 (unsigned int) timestamp );

	for( test_number = 0;
	     test_number < number_of_tests;
	     test_number++ )
	{
		random_number = rand();

		${library_name_suffix:upper_case}_TEST_ASSERT_GREATER_THAN_INT(
		 "random_number",
		 random_number,
		 -1 );

		if( ${type_size_name} > 0 )
		{
			read_offset = (off64_t) random_number % ${type_size_name};
		}
		read_size = (size_t) random_number % ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE;

#if defined( ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_VERBOSE )
		fprintf(
		 stdout,
		 "${library_name}_${type_name}_read_buffer_at_offset: at offset: %" PRIi64 " (0x%08" PRIx64 ") of size: %" PRIzd "\n",
		 read_offset,
		 read_offset,
		 read_size );
#endif
		read_count = ${library_name}_${type_name}_read_buffer_at_offset(
		              ${type_name},
		              buffer,
		              read_size,
		              read_offset,
		              &error );

		remaining_${type_size_name} = ${type_size_name} - read_offset;

		if( read_size > remaining_${type_size_name} )
		{
			read_size = (size_t) remaining_${type_size_name};
		}
		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) read_size );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		read_offset += read_count;

		result = ${library_name}_${type_name}_get_offset(
		          ${type_name},
		          &offset,
		          &error );

		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
		 "offset",
		 offset,
		 read_offset );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );
	}
	/* Test error cases
	 */
	read_count = ${library_name}_${type_name}_read_buffer_at_offset(
	              NULL,
	              buffer,
	              ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE,
	              0,
	              &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_SSIZE(
	 "read_count",
	 read_count,
	 (ssize_t) -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	read_count = ${library_name}_${type_name}_read_buffer_at_offset(
	              ${type_name},
	              NULL,
	              ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE,
	              0,
	              &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_SSIZE(
	 "read_count",
	 read_count,
	 (ssize_t) -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
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

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_SSIZE(
	 "read_count",
	 read_count,
	 (ssize_t) -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	read_count = ${library_name}_${type_name}_read_buffer_at_offset(
	              ${type_name},
	              buffer,
	              ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE,
	              -1,
	              &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_SSIZE(
	 "read_count",
	 read_count,
	 (ssize_t) -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

#if defined( HAVE_${library_name_suffix:upper_case}_TEST_RWLOCK )

	/* Test ${library_name}_${type_name}_read_buffer_at_offset with pthread_rwlock_wrlock failing in libcthreads_read_write_lock_grab_for_write
	 */
	${library_name_suffix}_test_pthread_rwlock_wrlock_attempts_before_fail = 0;

	read_count = ${library_name}_${type_name}_read_buffer_at_offset(
	              ${type_name},
	              buffer,
	              ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE,
	              0,
	              &error );

	if( ${library_name_suffix}_test_pthread_rwlock_wrlock_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_pthread_rwlock_wrlock_attempts_before_fail = -1;
	}
	else
	{
		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) -1 );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
	/* Test ${library_name}_${type_name}_read_buffer_at_offset with pthread_rwlock_unlock failing in libcthreads_read_write_lock_release_for_write
	 */
	${library_name_suffix}_test_pthread_rwlock_unlock_attempts_before_fail = 0;

	read_count = ${library_name}_${type_name}_read_buffer_at_offset(
	              ${type_name},
	              buffer,
	              ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_READ_BUFFER_SIZE,
	              0,
	              &error );

	if( ${library_name_suffix}_test_pthread_rwlock_unlock_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_pthread_rwlock_unlock_attempts_before_fail = -1;
	}
	else
	{
		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_SSIZE(
		 "read_count",
		 read_count,
		 (ssize_t) -1 );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
#endif /* defined( HAVE_${library_name_suffix:upper_case}_TEST_RWLOCK ) */

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	return( 0 );
}

