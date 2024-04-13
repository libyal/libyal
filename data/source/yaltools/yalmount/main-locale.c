
#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBOSXFUSE )
	struct fuse_operations ${mount_tool_name}_fuse_operations;

#if FUSE_USE_VERSION >= 30
	/* Need to set this to 1 even if there no arguments, otherwise this causes
	 * fuse: empty argv passed to fuse_session_new()
	 */
	char *fuse_argv[ 2 ]                               = { program, NULL };
	struct fuse_args ${mount_tool_name}_fuse_arguments = FUSE_ARGS_INIT(1, fuse_argv);
#else
	struct fuse_args ${mount_tool_name}_fuse_arguments = FUSE_ARGS_INIT(0, NULL);
	struct fuse_chan *${mount_tool_name}_fuse_channel  = NULL;
#endif
	struct fuse *${mount_tool_name}_fuse_handle        = NULL;

#elif defined( HAVE_LIBDOKAN )
	DOKAN_OPERATIONS ${mount_tool_name}_dokan_operations;
	DOKAN_OPTIONS ${mount_tool_name}_dokan_options;
#endif

	libcnotify_stream_set(
	 stderr,
	 NULL );
	libcnotify_verbose_set(
	 1 );

	if( libclocale_initialize(
	     "${tools_name}",
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to initialize locale values.\n" );

		goto on_error;
	}
	if( ${tools_name}_output_initialize(
	     _IONBF,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to initialize output settings.\n" );

		goto on_error;
	}
	${tools_name}_output_version_fprint(
	 stdout,
	 program );

