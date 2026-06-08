${mount_tool_options_variable_declarations}
	system_character_t *source      = NULL;
	char *program                   = "${mount_tool_name}";
	system_integer_t option         = 0;
	int number_of_options           = (int) ( sizeof( options ) / sizeof( ${tools_name}_option_t ) );
	int verbose                     = 0;

#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBFUSE3 ) || defined( HAVE_LIBOSXFUSE ) || defined( HAVE_LIBDOKAN )
	system_character_t *mount_point = NULL;
	int result                      = 0;
#endif
