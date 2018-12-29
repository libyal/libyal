/* Retrieves the number of ${mount_tool_file_entry_type_description}s
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_number_of_${mount_tool_file_entry_type}s(
     mount_file_system_t *file_system,
     int *number_of_${mount_tool_file_entry_type}s,
     libcerror_error_t **error )
{
	static char *function = "mount_file_system_get_number_of_${mount_tool_file_entry_type}s";

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
	if( libcdata_array_get_number_of_entries(
	     file_system->${mount_tool_file_entry_type}s_array,
	     number_of_${mount_tool_file_entry_type}s,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of ${mount_tool_file_entry_type_description}s.",
		 function );

		return( -1 );
	}
	return( 1 );
}

