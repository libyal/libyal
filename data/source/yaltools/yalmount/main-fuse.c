#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBOSXFUSE )
	if( option_extended_options != NULL )
	{
		/* This argument is required but ignored
		 */
		if( fuse_opt_add_arg(
		     &${mount_tool_name}_fuse_arguments,
		     "" ) != 0 )
		{
			fprintf(
			 stderr,
			 "Unable add fuse arguments.\n" );

			goto on_error;
		}
		if( fuse_opt_add_arg(
		     &${mount_tool_name}_fuse_arguments,
		     "-o" ) != 0 )
		{
			fprintf(
			 stderr,
			 "Unable add fuse arguments.\n" );

			goto on_error;
		}
		if( fuse_opt_add_arg(
		     &${mount_tool_name}_fuse_arguments,
		     option_extended_options ) != 0 )
		{
			fprintf(
			 stderr,
			 "Unable add fuse arguments.\n" );

			goto on_error;
		}
	}
	if( memory_set(
	     &${mount_tool_name}_fuse_operations,
	     0,
	     sizeof( struct fuse_operations ) ) == NULL )
	{
		fprintf(
		 stderr,
		 "Unable to clear fuse operations.\n" );

		goto on_error;
	}
	${mount_tool_name}_fuse_operations.open       = &mount_fuse_open;
	${mount_tool_name}_fuse_operations.read       = &mount_fuse_read;
	${mount_tool_name}_fuse_operations.release    = &mount_fuse_release;
	${mount_tool_name}_fuse_operations.opendir    = &mount_fuse_opendir;
	${mount_tool_name}_fuse_operations.readdir    = &mount_fuse_readdir;
	${mount_tool_name}_fuse_operations.releasedir = &mount_fuse_releasedir;
	${mount_tool_name}_fuse_operations.getattr    = &mount_fuse_getattr;
	${mount_tool_name}_fuse_operations.destroy    = &mount_fuse_destroy;

#if FUSE_USE_VERSION >= 30
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
#endif /* FUSE_USE_VERSION >= 30 */

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

