#if !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 )
	if( source != NULL )
	{
		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_${type_name}_open",
		 ${library_name_suffix}_test_${type_name}_open,
		 source );

#if defined( HAVE_WIDE_CHARACTER_TYPE )

		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_${type_name}_open_wide",
		 ${library_name_suffix}_test_${type_name}_open_wide,
		 source );

#endif /* defined( HAVE_WIDE_CHARACTER_TYPE ) */

#if defined( ${library_name_upper_case}_HAVE_BFIO )

		/* TODO add test for ${library_name}_${type_name}_open_file_io_handle */

#endif /* defined( ${library_name_upper_case}_HAVE_BFIO ) */

		${library_name_suffix_upper_case}_TEST_RUN(
		 "${library_name}_${type_name}_close",
		 ${library_name_suffix}_test_${type_name}_close );

		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_${type_name}_open_close",
		 ${library_name_suffix}_test_${type_name}_open_close,
		 source );

		/* Initialize test
		 */
		result = ${library_name_suffix}_test_${type_name}_open_source(
		          &${type_name},
		          source,
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

