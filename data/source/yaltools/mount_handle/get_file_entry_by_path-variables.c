	${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type} = NULL;
	const system_character_t *filename                                             = NULL;
	static char *function                                                          = "mount_handle_get_file_entry_by_path";
	size_t filename_length                                                         = 0;
	size_t path_index                                                              = 0;
	size_t path_length                                                             = 0;
	int result                                                                     = 0;

