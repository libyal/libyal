#if !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 )
	if( source != NULL )
	{
		string_length = system_string_length(
		                 source );

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		result = ${library_name}_glob_wide(
		          source,
		          string_length,
		          &filenames,
		          &number_of_filenames,
		          &error );
#else
		result = ${library_name}_glob(
		          source,
		          string_length,
		          &filenames,
		          &number_of_filenames,
		          &error );
#endif

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "filenames",
		 filenames );

		${library_name_suffix_upper_case}_TEST_ASSERT_GREATER_THAN_INT(
		 "number_of_filenames",
		 number_of_filenames,
		 0 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		result = libbfio_pool_initialize(
		          &file_io_pool,
		          number_of_filenames,
		          LIBBFIO_POOL_UNLIMITED_NUMBER_OF_OPEN_HANDLES,
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

	        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	         "file_io_pool",
	         file_io_pool );

	        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	         "error",
	         error );

		for( filename_index = 0;
		     filename_index < number_of_filenames;
		     filename_index++ )
		{
			result = libbfio_file_initialize(
			          &file_io_handle,
			          &error );

			${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
			 "result",
			 result,
			 1 );

		        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		         "file_io_handle",
		         file_io_handle );

		        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		         "error",
		         error );

			string_length = system_string_length(
			                 filenames[ filename_index ] );

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
			result = libbfio_file_set_name_wide(
			          file_io_handle,
			          filenames[ filename_index ],
			          string_length,
			          &error );
#else
			result = libbfio_file_set_name(
			          file_io_handle,
			          filenames[ filename_index ],
			          string_length,
			          &error );
#endif
			${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
			 "result",
			 result,
			 1 );

			${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
			 "error",
			 error );

			result = libbfio_pool_set_handle(
			          file_io_pool,
			          filename_index,
			          file_io_handle,
			          LIBBFIO_OPEN_READ,
			          &error );

			${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
			 "result",
			 result,
			 1 );

		        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		         "error",
		         error );

			file_io_handle = NULL;
		}
