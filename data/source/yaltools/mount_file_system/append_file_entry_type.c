/* Appends a ${mount_tool_file_entry_type_description} to the file system
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_append_${mount_tool_file_entry_type}(
     mount_file_system_t *file_system,
     ${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type_name},
     libcerror_error_t **error )
{
	static char *function = "mount_file_system_append_${mount_tool_file_entry_type}";
	int entry_index       = 0;

	if( file_system == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file system.",
		 function );

		return( -1 );
	}
	if( libcdata_array_append_entry(
	     file_system->${mount_tool_file_entry_type}s_array,
	     &entry_index,
	     (intptr_t *) ${mount_tool_file_entry_type_name},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_APPEND_FAILED,
		 "%s: unable to append ${mount_tool_file_entry_type_description} to array.",
		 function );

		return( -1 );
	}
	return( 1 );
}

