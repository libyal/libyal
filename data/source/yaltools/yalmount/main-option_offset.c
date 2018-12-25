	if( option_offset != NULL )
	{
		if( mount_handle_set_offset(
		     ${mount_tool_name}_mount_handle,
		     option_offset,
		     &error ) != 1 )
		{
			fprintf(
			 stderr,
			 "Unable to set ${mount_tool_source_type} offset.\n" );

			goto on_error;
		}
	}
