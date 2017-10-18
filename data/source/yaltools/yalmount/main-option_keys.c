	if( option_keys != NULL )
	{
		if( mount_handle_set_keys(
		     ${mount_tool_name}_mount_handle,
		     option_keys,
		     &error ) != 1 )
		{
			fprintf(
			 stderr,
			 "Unable to set keys.\n" );

			goto on_error;
		}
	}
