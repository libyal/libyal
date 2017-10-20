#if !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 )
	if( source != NULL )
	{
		result = libbfio_file_range_initialize(
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
		                 source );

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		result = libbfio_file_range_set_name_wide(
		          file_io_handle,
		          source,
		          string_length,
		          &error );
#else
		result = libbfio_file_range_set_name(
		          file_io_handle,
		          source,
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

		result = libbfio_file_range_set(
		          file_io_handle,
		          ${type_name}_offset,
		          0,
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

	        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	         "error",
	         error );

		result = ${library_name}_check_${type_name}_signature_file_io_handle(
		          file_io_handle,
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_NOT_EQUAL_INT(
		 "result",
		 result,
		 -1 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );
	}
	if( ( result != 0 )
	 && ( ${type_name}_offset == 0 ) )
	{
		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_${type_name}_open",
		 ${library_name_suffix}_test_${type_name}_open,
${test_options_macro_arguments} );

#if defined( HAVE_WIDE_CHARACTER_TYPE )

		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_${type_name}_open_wide",
		 ${library_name_suffix}_test_${type_name}_open_wide,
${test_options_macro_arguments} );

#endif /* defined( HAVE_WIDE_CHARACTER_TYPE ) */

		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_${type_name}_open_file_io_handle",
		 ${library_name_suffix}_test_${type_name}_open_file_io_handle,
${test_options_macro_arguments} );

		${library_name_suffix_upper_case}_TEST_RUN(
		 "${library_name}_${type_name}_close",
		 ${library_name_suffix}_test_${type_name}_close );

		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_${type_name}_open_close",
		 ${library_name_suffix}_test_${type_name}_open_close,
${test_options_macro_arguments} );
	}
	if( result != 0 )
	{
		/* Initialize ${type_name} for tests
		 */
		result = ${library_name_suffix}_test_${type_name}_open_source(
		          &${type_name},
${test_options_open_source_arguments},
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "${type_name}",
		 ${type_name} );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

