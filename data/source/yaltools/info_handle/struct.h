typedef struct info_handle info_handle_t;

struct info_handle
{
	/* The ${info_tool_source_type}
	 */
	${library_name}_${info_tool_source_type}_t *${info_tool_source_type};

	/* The ascii codepage
	 */
	int ascii_codepage;

	/* The notification output stream
	 */
	FILE *notify_stream;

	/* Value to indicate if abort was signalled
	 */
	int abort;
};

