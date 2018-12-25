	if( option_startup_key_filename != NULL )
	{
		if( mount_handle_read_startup_key(
		     ${mount_tool_name}_mount_handle,
		     option_startup_key_filename,
		     &error ) != 1 )
		{
			fprintf(
			 stderr,
			 "Unable to read startup key.\n" );

			goto on_error;
		}
	}
