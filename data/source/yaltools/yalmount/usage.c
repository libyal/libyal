mount_handle_t *${mount_tool_name}_mount_handle = NULL;
int ${mount_tool_name}_abort                    = 0;

/* Prints the executable usage information
 */
void usage_fprint(
      FILE *stream )
{
	if( stream == NULL )
	{
		return;
	}
	fprintf( stream, "Use ${mount_tool_name} to mount ${mount_tool_source_description_long}\n\n" );

${mount_tool_usage}

	fprintf( stream, "\t${mount_tool_source_type}: ${mount_tool_source_alignment}${mount_tool_source_description_long}\n\n" );
	fprintf( stream, "\tmount_point: the directory to serve as mount point\n\n" );

${mount_tool_options}
}

