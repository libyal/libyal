/* Retrieves the ${mount_tool_file_system_type_description}
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_${mount_tool_file_system_type}(
     mount_file_system_t *file_system,
     ${library_name}_${mount_tool_file_system_type}_t **${mount_tool_file_system_type},
     libcerror_error_t **error )
{
	static char *function = "mount_file_system_get_${mount_tool_file_system_type}";

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
	if( ${mount_tool_file_system_type} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${mount_tool_file_system_type}.",
		 function );

		return( -1 );
	}
	*${mount_tool_file_system_type} = file_system->${mount_tool_file_system_type};

	return( 1 );
}

