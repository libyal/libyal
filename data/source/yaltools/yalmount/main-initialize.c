	libcnotify_verbose_set(
	 verbose );
	${library_name}_notify_set_stream(
	 stderr,
	 NULL );
	${library_name}_notify_set_verbose(
	 verbose );

	if( mount_handle_initialize(
	     &${mount_tool_name}_mount_handle,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to initialize mount handle.\n" );

		goto on_error;
	}
