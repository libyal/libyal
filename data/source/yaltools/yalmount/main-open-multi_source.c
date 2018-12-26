	if( mount_handle_open(
	     ${mount_tool_name}_mount_handle,
	     sources,
	     number_of_sources,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to open source ${mount_tool_source_type}(s)\n" );

		goto on_error;
	}
