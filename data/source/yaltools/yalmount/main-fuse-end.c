	${mount_tool_name}_fuse_operations.destroy    = &mount_fuse_destroy;

#if defined( HAVE_LIBFUSE3 )
	${mount_tool_name}_fuse_handle = fuse_new(
	                                  &${mount_tool_name}_fuse_arguments,
	                                  &${mount_tool_name}_fuse_operations,
	                                  sizeof( struct fuse_operations ),
	                                  ${mount_tool_name}_mount_handle );

	if( ${mount_tool_name}_fuse_handle == NULL )
	{
		fprintf(
		 stderr,
		 "Unable to create fuse handle.\n" );

		goto on_error;
	}
	result = fuse_mount(
	          ${mount_tool_name}_fuse_handle,
	          mount_point );

	if( result != 0 )
	{
		fprintf(
		 stderr,
		 "Unable to fuse mount file system.\n" );

		goto on_error;
	}
#else
	${mount_tool_name}_fuse_channel = fuse_mount(
	                                   mount_point,
	                                   &${mount_tool_name}_fuse_arguments );

	if( ${mount_tool_name}_fuse_channel == NULL )
	{
		fprintf(
		 stderr,
		 "Unable to create fuse channel.\n" );

		goto on_error;
	}
	${mount_tool_name}_fuse_handle = fuse_new(
	                                  ${mount_tool_name}_fuse_channel,
	                                  &${mount_tool_name}_fuse_arguments,
	                                  &${mount_tool_name}_fuse_operations,
	                                  sizeof( struct fuse_operations ),
	                                  ${mount_tool_name}_mount_handle );

	if( ${mount_tool_name}_fuse_handle == NULL )
	{
		fprintf(
		 stderr,
		 "Unable to create fuse handle.\n" );

		goto on_error;
	}
#endif /* defined( HAVE_LIBFUSE3 ) */

	if( verbose == 0 )
	{
		if( fuse_daemonize(
		     0 ) != 0 )
		{
			fprintf(
			 stderr,
			 "Unable to daemonize fuse.\n" );

			goto on_error;
		}
	}
	result = fuse_loop(
	          ${mount_tool_name}_fuse_handle );

	if( result != 0 )
	{
		fprintf(
		 stderr,
		 "Unable to run fuse loop.\n" );

		goto on_error;
	}
	fuse_destroy(
	 ${mount_tool_name}_fuse_handle );

	fuse_opt_free_args(
	 &${mount_tool_name}_fuse_arguments );

	return( EXIT_SUCCESS );

