	if( mount_handle_open(
	     ${mount_tool_name}_mount_handle,
	     source,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to open source ${mount_tool_source_type}.\n" );

		goto on_error;
	}
