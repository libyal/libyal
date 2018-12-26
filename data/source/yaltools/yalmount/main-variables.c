	${library_name}_error_t *error        = NULL;
	system_character_t *mount_point       = NULL;
	const system_character_t *path_prefix = NULL;
	system_character_t *source            = NULL;
	char *program                         = "${mount_tool_name}";
${mount_tool_options_variable_declarations}
	system_integer_t option               = 0;
	size_t path_prefix_size               = 0;
	int result                            = 0;
	int verbose                           = 0;
