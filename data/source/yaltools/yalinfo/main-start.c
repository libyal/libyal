/* The main program
 */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
int wmain( int argc, wchar_t * const argv[] )
#else
int main( int argc, char * const argv[] )
#endif
{
	${library_name}_error_t *error = NULL;
${info_tool_options_variable_declarations}
	system_character_t *source     = NULL;
	char *program                  = "${info_tool_name}";
	system_integer_t option        = 0;
	int result                     = 0;
	int verbose                    = 0;

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
	${library_name_suffix}output_version_fprint(
	 stdout,
	 program );

	while( ( option = ${tools_name}_getopt(
	                   argc,
	                   argv,
	                   _SYSTEM_STRING( "c:hvV" ) ) ) != (system_integer_t) -1 )
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

${info_tool_options_switch}
		}
	}
	if( optind == argc )
	{
		fprintf(
		 stderr,
		 "Missing source ${info_tool_source_type}.\n" );

		usage_fprint(
		 stdout );

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
