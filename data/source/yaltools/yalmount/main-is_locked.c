	if( mount_handle_is_locked(
	     ${mount_tool_name}_mount_handle,
	     &error ) != 0 )
	{
		fprintf(
		 stderr,
		 "Unable to unlock: %" PRIs_SYSTEM "\n",
		 source );

		goto on_error;
	}
