	if( info_handle_open_input(
	     ${info_tool_name}_info_handle,
	     source,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to open: %" PRIs_SYSTEM ".\n",
		 source );

		goto on_error;
	}
	if( info_handle_${info_tool_source_type}_fprint(
	     ${info_tool_name}_info_handle,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to print ${info_tool_source_type} information.\n" );

		goto on_error;
	}
	if( info_handle_close_input(
	     ${info_tool_name}_info_handle,
	     &error ) != 0 )
	{
		fprintf(
		 stderr,
		 "Unable to close info handle.\n" );

		goto on_error;
	}
	if( info_handle_free(
	     &${info_tool_name}_info_handle,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to free info handle.\n" );

		goto on_error;
	}
	return( EXIT_SUCCESS );

on_error:
	if( error != NULL )
	{
		libcnotify_print_error_backtrace(
		 error );
		libcerror_error_free(
		 &error );
	}
	if( ${info_tool_name}_info_handle != NULL )
	{
		info_handle_free(
		 &${info_tool_name}_info_handle,
		 NULL );
	}
	return( EXIT_FAILURE );
}

