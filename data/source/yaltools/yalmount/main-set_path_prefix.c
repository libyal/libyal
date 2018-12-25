#if defined( WINAPI )
	path_prefix = _SYSTEM_STRING( "\\${mount_tool_path_prefix_upper_case}" );
#else
	path_prefix = _SYSTEM_STRING( "/${mount_tool_path_prefix}" );
#endif
	path_prefix_size = 1 + system_string_length(
	                        path_prefix );

	if( mount_handle_set_path_prefix(
	     ${mount_tool_name}_mount_handle,
	     path_prefix,
	     path_prefix_size,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to set path prefix.\n" );

		goto on_error;
	}
