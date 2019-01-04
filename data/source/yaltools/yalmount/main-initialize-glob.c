#if !defined( HAVE_GLOB_H )
	if( ${tools_name}_glob_initialize(
	     &glob,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to initialize glob.\n" );

		goto on_error;
	}
	if( ${tools_name}_glob_resolve(
	     glob,
	     &( argv[ optind ] ),
	     argc - optind - 1,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to resolve glob.\n" );

		goto on_error;
	}
	if( ${tools_name}_glob_get_results(
	     glob,
	     &number_of_sources,
	     (system_character_t ***) &sources,
	     &error ) != 1 )
	{
		fprintf(
		 stderr,
		 "Unable to retrieve glob results.\n" );

		goto on_error;
	}
#else
	sources           = &( argv[ optind ] );
	number_of_sources = argc - optind - 1;
#endif

