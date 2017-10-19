		/* Clean up
		 */
		result = ${library_name_suffix}_test_${type_name}_close_source(
		          &${type_name},
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 0 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "${type_name}",
		 ${type_name} );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		result = libbfio_handle_free(
		          &file_io_handle,
		          &error );

		LNK_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

		LNK_TEST_ASSERT_IS_NULL(
	         "file_io_handle",
	         file_io_handle );

	        LNK_TEST_ASSERT_IS_NULL(
	         "error",
	         error );
	}
#endif /* !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 ) */

