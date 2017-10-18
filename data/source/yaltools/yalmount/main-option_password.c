	if( option_password != NULL )
	{
		if( mount_handle_set_password(
		     ${mount_tool_name}_mount_handle,
		     option_password,
		     &error ) != 1 )
		{
			fprintf(
			 stderr,
			 "Unable to set password.\n" );

			goto on_error;
		}
	}
