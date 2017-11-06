info_handle_t *${info_tool_name}_info_handle = NULL;
int ${info_tool_name}_abort                  = 0;

/* Prints usage information
 */
void usage_fprint(
      FILE *stream )
{
	if( stream == NULL )
	{
		return;
	}
	fprintf( stream, "Use ${info_tool_name} to determine information about ${info_tool_source_description}.\n\n" );

${info_tool_usage}

	fprintf( stream, "\tsource: the source file\n\n" );

${info_tool_options}
}

