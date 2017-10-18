#endif

/* The main program
 */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
int wmain( int argc, wchar_t * const argv[] )
#else
int main( int argc, char * const argv[] )
#endif
{
	${library_name}_error_t *error                      = NULL;
	system_character_t *mount_point             = NULL;
${mount_tool_options_variable_declarations}
	system_character_t *source                  = NULL;
	char *program                               = "${mount_tool_name}";
	system_integer_t option                     = 0;
	int result                                  = 0;
	int verbose                                 = 0;

#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBOSXFUSE )
	struct fuse_operations ${mount_tool_name}_fuse_operations;

	struct fuse_args ${mount_tool_name}_fuse_arguments   = FUSE_ARGS_INIT(0, NULL);
	struct fuse_chan *${mount_tool_name}_fuse_channel    = NULL;
	struct fuse *${mount_tool_name}_fuse_handle          = NULL;

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

	while( ( option = ${tools_name}_getopt(
	                   argc,
	                   argv,
	                   _SYSTEM_STRING( "${mount_tool_getopt_string}" ) ) ) != (system_integer_t) -1 )
	{
		switch( option )
		{
			case (system_integer_t) '?':
			default:
				fprintf(
				 stderr,
				 "Invalid argument: %" PRIs_SYSTEM "\n",
				 argv[ optind - 1 ] );

				usage_fprint(
				 stdout );

				return( EXIT_FAILURE );

${mount_tool_options_switch}
		}
	}
	if( optind == argc )
	{
		fprintf(
		 stderr,
		 "Missing source ${mount_tool_source_type}.\n" );

		usage_fprint(
		 stdout );

		return( EXIT_FAILURE );
	}
	source = argv[ optind++ ];

	if( optind == argc )
	{
		fprintf(
		 stderr,
		 "Missing mount point.\n" );

		usage_fprint(
		 stdout );

		return( EXIT_FAILURE );
	}
	mount_point = argv[ optind ];

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
