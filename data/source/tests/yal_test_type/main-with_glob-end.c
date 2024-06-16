		/* Clean up
		 */
		result = ${library_name_suffix}_test_${type_name}_close_source(
		          &${type_name},
		          &error );

		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 0 );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
		 "${type_name}",
		 ${type_name} );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		result = libbfio_${bfio_type}_free(
		          &file_io_${bfio_type},
		          &error );

		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	         "file_io_${bfio_type}",
	         file_io_${bfio_type} );

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

		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );
	}
#endif /* !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 ) */

