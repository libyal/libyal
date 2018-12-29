/* Retrieves a specific ${mount_tool_file_entry_type_description}
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_${mount_tool_file_entry_type}_by_index(
     mount_file_system_t *file_system,
     int ${mount_tool_file_entry_type}_index,
     ${library_name}_${mount_tool_file_entry_type}_t **${mount_tool_file_entry_type},
     libcerror_error_t **error )
{
	static char *function = "mount_file_system_get_${mount_tool_file_entry_type}_by_index";

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
	if( libcdata_array_get_entry_by_index(
	     file_system->${mount_tool_file_entry_type}s_array,
	     ${mount_tool_file_entry_type}_index,
	     (intptr_t **) ${mount_tool_file_entry_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_entry_type_description}: %d.",
		 function,
		 ${mount_tool_file_entry_type}_index );

		return( -1 );
	}
	return( 1 );
}

