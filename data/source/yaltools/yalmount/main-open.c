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
