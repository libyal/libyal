/* Tests the ${library_name}_${type_name}_open_file_io_pool function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_open_file_io_pool(
${test_options_function_arguments} )
{
	${library_name}_${type_name}_t *${type_name} = NULL;
	libbfio_handle_t *file_io_handle             = NULL;
	libbfio_pool_t *file_io_pool                 = NULL;
	libcerror_error_t *error                     = NULL;
	system_character_t **filenames               = NULL;
	size_t string_length                         = 0;
	int filename_index                           = 0;
	int number_of_filenames                      = 0;
	int result                                   = 0;

	/* Initialize test
	 */
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

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "filenames",
	 filenames );

	${library_name_suffix:upper_case}_TEST_ASSERT_GREATER_THAN_INT(
	 "number_of_filenames",
	 number_of_filenames,
	 0 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = libbfio_pool_initialize(
	          &file_io_pool,
	          number_of_filenames,
	          LIBBFIO_POOL_UNLIMITED_NUMBER_OF_OPEN_HANDLES,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "file_io_pool",
	 file_io_pool );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	for( filename_index = 0;
	     filename_index < number_of_filenames;
	     filename_index++ )
	{
		result = libbfio_file_initialize(
		          &file_io_handle,
		          &error );

		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

	        ${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	         "file_io_handle",
	         file_io_handle );

	        ${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
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
		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

		${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

		result = libbfio_pool_set_handle(
		          file_io_pool,
		          filename_index,
		          file_io_handle,
		          LIBBFIO_OPEN_READ,
		          &error );

		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

	        ${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	         "error",
	         error );

		file_io_handle = NULL;
	}
	result = ${library_name}_${type_name}_initialize(
	          &${type_name},
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "${type_name}",
	 ${type_name} );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

