#if !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 )

	${library_name_suffix:upper_case}_TEST_RUN_WITH_ARGS(
	 "${library_name}_check_${signature_type}_signature",
	 ${library_name_suffix}_test_check_${signature_type}_signature,
	 source );

#if defined( HAVE_WIDE_CHARACTER_TYPE )

	${library_name_suffix:upper_case}_TEST_RUN_WITH_ARGS(
	 "${library_name}_check_${signature_type}_signature_wide",
	 ${library_name_suffix}_test_check_${signature_type}_signature_wide,
	 source );

#endif /* defined( HAVE_WIDE_CHARACTER_TYPE ) */

	${library_name_suffix:upper_case}_TEST_RUN_WITH_ARGS(
	 "${library_name}_check_${signature_type}_signature_file_io_handle",
	 ${library_name_suffix}_test_check_${signature_type}_signature_file_io_handle,
	 source );

#endif /* !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 ) */

	return( EXIT_SUCCESS );

on_error:
	return( EXIT_FAILURE );
}

