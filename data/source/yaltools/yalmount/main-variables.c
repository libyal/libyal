	${library_name}_error_t *error  = NULL;
	system_character_t *mount_point = NULL;
	system_character_t *program     = _SYSTEM_STRING( "${mount_tool_name}" );
	system_character_t *source      = NULL;
${mount_tool_options_variable_declarations}
	system_integer_t option         = 0;
	int result                      = 0;
	int verbose                     = 0;
