#else
	fprintf(
	 stderr,
	 "No sub system to mount ${library_name_suffix_upper_case} format.\n" );

	return( EXIT_FAILURE );
#endif

on_error:
	if( error != NULL )
	{
		libcnotify_print_error_backtrace(
		 error );
		libcerror_error_free(
		 &error );
	}
#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBOSXFUSE )
	if( ${mount_tool_name}_fuse_handle != NULL )
	{
		fuse_destroy(
		 ${mount_tool_name}_fuse_handle );
	}
	fuse_opt_free_args(
	 &${mount_tool_name}_fuse_arguments );
#endif
	if( ${mount_tool_name}_mount_handle != NULL )
	{
		mount_handle_free(
		 &${mount_tool_name}_mount_handle,
		 NULL );
	}
	return( EXIT_FAILURE );
}

