/* Tests the ${library_name}_${type_name}_seek_offset function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_seek_offset(
     ${library_name}_${type_name}_t *${type_name} )
{
	libcerror_error_t *error = NULL;
	size64_t size            = 0;
	off64_t offset           = 0;

	/* Test regular cases
	 */
	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          0,
	          SEEK_END,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_NOT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	size = (size64_t) offset;

	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          1024,
	          SEEK_SET,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) 1024 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          -512,
	          SEEK_CUR,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) 512 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          (off64_t) ( size + 512 ),
	          SEEK_SET,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) ( size + 512 ) );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Reset offset to 0
	 */
	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          0,
	          SEEK_SET,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) 0 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test error cases
	 */
	offset = ${library_name}_${type_name}_seek_offset(
	          NULL,
	          0,
	          SEEK_SET,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          -1,
	          SEEK_SET,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          -1,
	          SEEK_CUR,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          (off64_t) ( -1 * ( size + 1 ) ),
	          SEEK_END,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
	 "offset",
	 offset,
	 (int64_t) -1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

#if defined( HAVE_${library_name_suffix:upper_case}_TEST_RWLOCK )

	/* Test ${library_name}_${type_name}_seek_offset with pthread_rwlock_wrlock failing in libcthreads_read_write_lock_grab_for_write
	 */
	${library_name_suffix}_test_pthread_rwlock_wrlock_attempts_before_fail = 0;

	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          0,
	          SEEK_SET,
	          &error );

	if( ${library_name_suffix}_test_pthread_rwlock_wrlock_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_pthread_rwlock_wrlock_attempts_before_fail = -1;
	}
	else
	{
		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
		 "offset",
		 (int64_t) offset,
		 (int64_t) -1 );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
	/* Test ${library_name}_${type_name}_seek_offset with pthread_rwlock_unlock failing in libcthreads_read_write_lock_release_for_write
	 */
	${library_name_suffix}_test_pthread_rwlock_unlock_attempts_before_fail = 0;

	offset = ${library_name}_${type_name}_seek_offset(
	          ${type_name},
	          0,
	          SEEK_SET,
	          &error );

	if( ${library_name_suffix}_test_pthread_rwlock_unlock_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_pthread_rwlock_unlock_attempts_before_fail = -1;
	}
	else
	{
		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT64(
		 "offset",
		 (int64_t) offset,
		 (int64_t) -1 );

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

