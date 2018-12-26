	if( mount_handle_is_locked(
	     ${mount_tool_name}_mount_handle,
	     &error ) != 0 )
	{
		fprintf(
		 stderr,
		 "Unable to unlock source ${mount_tool_source_type}\n" );

		goto on_error;
	}
