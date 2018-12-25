	if( option_recovery_password != NULL )
	{
		if( mount_handle_set_recovery_password(
		     ${mount_tool_name}_mount_handle,
		     option_recovery_password,
		     &error ) != 1 )
		{
			fprintf(
			 stderr,
			 "Unable to set recovery password.\n" );

			goto on_error;
		}
	}
