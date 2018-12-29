/* Retrieves the path from a ${mount_tool_file_entry_type_description} index.
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_path_from_${mount_tool_file_entry_type}_index(
     mount_file_system_t *file_system,
     int ${mount_tool_file_entry_type}_index,
     system_character_t *path,
     size_t path_size,
     libcerror_error_t **error )
{
	static char *function                    = "mount_file_system_get_path_from_${mount_tool_file_entry_type}_index";
	size_t path_index                        = 0;
	size_t required_path_size                = 0;
	int ${mount_tool_file_entry_type}_number = 0;

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
	if( file_system->path_prefix == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
		 "%s: invalid file system - missing path prefix.",
		 function );

		return( -1 );
	}
	if( path == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid path.",
		 function );

		return( -1 );
	}
	if( path_size > (size_t) SSIZE_MAX )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid path length value exceeds maximum.",
		 function );

		return( -1 );
	}
        required_path_size = file_system->path_prefix_size;

	${mount_tool_file_entry_type}_number = ${mount_tool_file_entry_type}_index + 1;

	while( ${mount_tool_file_entry_type}_number > 0 )
	{
		required_path_size++;

		${mount_tool_file_entry_type}_number /= 10;
	}
	if( path_size <= required_path_size )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_TOO_SMALL,
		 "%s: invalid path size value too small.",
		 function );

		return( -1 );
	}
	if( system_string_copy(
	     path,
	     file_system->path_prefix,
	     file_system->path_prefix_size ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_COPY_FAILED,
		 "%s: unable to copy path prefix.",
		 function );

		return( -1 );
	}
	path_index = required_path_size - 1;

	${mount_tool_file_entry_type}_number = ${mount_tool_file_entry_type}_index + 1;

	path[ path_index-- ] = 0;

	while( ${mount_tool_file_entry_type}_number > 0 )
	{
		path[ path_index-- ] = (system_character_t) '0' + ( ${mount_tool_file_entry_type}_number % 10 );

		${mount_tool_file_entry_type}_number /= 10;
	}
	return( 1 );
}

