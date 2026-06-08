${info_tool_options_variable_declarations}
	system_character_t *source     = NULL;
	char *program                  = "${info_tool_name}";
	system_integer_t option        = 0;
	int number_of_options          = (int) ( sizeof( options ) / sizeof( ${tools_name}_option_t ) );
	int verbose                    = 0;

#if defined( __MINGW32__ ) && defined( HAVE_MINGW_BINMODE )
	_setmode( _fileno( stdout ), _O_BINARY );
	_setmode( _fileno( stderr ), _O_BINARY );
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

	if( ${tools_name}_getopt_get_options_string(
	     options,
	     number_of_options,
	     options_string,
	     32 ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to determine options string.\n" );

		goto on_error;
	}
	while( ( option = ${tools_name}_getopt(
	                   argc,
	                   argv,
	                   options_string ) ) != (system_integer_t) -1 )
	{
		switch( option )
		{
			case (system_integer_t) '?':
			default:
				fprintf(
				 stderr,
				 "Invalid argument: %" PRIs_SYSTEM "\n",
				 argv[ optind - 1 ] );

				${tools_name}_getopt_usage_fprint(
				 stdout,
				 program,
				 description,
				 options,
				 number_of_options );

				return( EXIT_FAILURE );

${info_tool_options_switch}
		}
	}
	if( optind == argc )
	{
		fprintf(
		 stderr,
		 "Missing source ${info_tool_source_type}.\n" );

		${tools_name}_getopt_usage_fprint(
		 stdout,
		 program,
		 description,
		 options,
		 number_of_options );

		return( EXIT_FAILURE );
	}
	source = argv[ optind ];

	libcnotify_verbose_set(
	 verbose );
	${library_name}_notify_set_stream(
	 stderr,
	 NULL );
	${library_name}_notify_set_verbose(
	 verbose );

	if( info_handle_initialize(
	     &${info_tool_name}_info_handle,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to initialize info handle.\n" );

		goto on_error;
	}
