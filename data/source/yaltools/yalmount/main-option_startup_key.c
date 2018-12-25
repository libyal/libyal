	if( option_startup_key_path != NULL )
	{
		if( mount_handle_set_startup_key(
		     ${mount_tool_name}_mount_handle,
		     option_startup_key_path,
		     &error ) != 1 )
		{
			fprintf(
			 stderr,
			 "Unable to set startup key.\n" );

			goto on_error;
		}
	}
