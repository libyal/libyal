#if defined( WINAPI )
	path_prefix = _SYSTEM_STRING( "\\${library_name_suffix_upper_case}" );
#else
	path_prefix = _SYSTEM_STRING( "/${library_name_suffix}" );
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
	if( mount_handle_open(
	     ${mount_tool_name}_mount_handle,
	     source,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to open: %" PRIs_SYSTEM "\n",
		 source );

		goto on_error;
	}
	if( mount_handle_is_locked(
	     ${mount_tool_name}_mount_handle,
	     &error ) != 0 )
	{
		fprintf(
		 stderr,
		 "Unable to unlock: %" PRIs_SYSTEM "\n",
		 source );

		goto on_error;
	}
