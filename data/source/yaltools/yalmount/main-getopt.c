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

${mount_tool_options_switch}
		}
	}
	if( optind == argc )
	{
		fprintf(
		 stderr,
		 "Missing source ${mount_tool_source_type}.\n" );

		${tools_name}_getopt_usage_fprint(
		 stdout,
		 program,
		 description,
		 options,
		 number_of_options );

		return( EXIT_FAILURE );
	}
	source = argv[ optind++ ];

	if( optind == argc )
	{
		fprintf(
		 stderr,
		 "Missing mount point.\n" );

		${tools_name}_getopt_usage_fprint(
		 stdout,
		 program,
		 description,
		 options,
		 number_of_options );

		return( EXIT_FAILURE );
	}
#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBFUSE3 ) || defined( HAVE_LIBOSXFUSE ) || defined( HAVE_LIBDOKAN )
	mount_point = argv[ optind ];
#endif
