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

/* Retrieves the mounted timestamp
 * On Windows the timestamp is an unsigned 64-bit FILETIME timestamp
 * otherwise the timestamp is a signed 64-bit POSIX date and time value in number of nanoseconds
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_mounted_timestamp(
     mount_file_system_t *file_system,
     uint64_t *mounted_timestamp,
     libcerror_error_t **error )
{
	static char *function = "mount_file_system_get_mounted_timestamp";

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
	if( mounted_timestamp == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mounted timestamp.",
		 function );

		return( -1 );
	}
	*mounted_timestamp = file_system->mounted_timestamp;

	return( 1 );
}

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

/* Appends a ${mount_tool_file_entry_type_description} to the file system
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_append_${mount_tool_file_entry_type}(
     mount_file_system_t *file_system,
     ${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type},
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
	     (intptr_t *) ${mount_tool_file_entry_type},
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

/* Retrieves the ${mount_tool_file_entry_type_description} index from a path
 * Returns 1 if successful, 0 if no such ${mount_tool_file_entry_type_description} index or -1 on error
 */
int mount_file_system_get_${mount_tool_file_entry_type}_index_from_path(
     mount_file_system_t *file_system,
     const system_character_t *path,
     size_t path_length,
     int *${mount_tool_file_entry_type}_index,
     libcerror_error_t **error )
{
	static char *function                    = "mount_file_system_get_${mount_tool_file_entry_type}_index_from_path";
	system_character_t character             = 0;
	size_t path_index                        = 0;
	int ${mount_tool_file_entry_type}_number = 0;
	int result                               = 0;

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
	if( path_length > (size_t) ( SSIZE_MAX - 1 ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid path length value exceeds maximum.",
		 function );

		return( -1 );
	}
	if( ${mount_tool_file_entry_type}_index == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${mount_tool_file_entry_type_description} index.",
		 function );

		return( -1 );
	}
	path_length = system_string_length(
	               path );

	if( ( path_length == 1 )
	 && ( path[ 0 ] == file_system->path_prefix[ 0 ] ) )
	{
		*${mount_tool_file_entry_type}_index = -1;

		return( 1 );
	}
	if( ( path_length < file_system->path_prefix_size )
	 || ( path_length > ( file_system->path_prefix_size + 3 ) ) )
	{
		return( 0 );
	}
#if defined( WINAPI )
	result = system_string_compare_no_case(
	          path,
	          file_system->path_prefix,
	          file_system->path_prefix_size - 1 );
#else
	result = system_string_compare(
	          path,
	          file_system->path_prefix,
	          file_system->path_prefix_size - 1 );
#endif
	if( result != 0 )
	{
		return( 0 );
	}
	${mount_tool_file_entry_type}_number = 0;

	path_index = file_system->path_prefix_size - 1;

	while( path_index < path_length )
	{
		character = path[ path_index++ ];

		if( ( character < (system_character_t) '0' )
		 || ( character > (system_character_t) '9' ) )
		{
			return( 0 );
		}
		${mount_tool_file_entry_type}_number *= 10;
		${mount_tool_file_entry_type}_number += character - (system_character_t) '0';
	}
	*${mount_tool_file_entry_type}_index = ${mount_tool_file_entry_type}_number - 1;

	return( 1 );
}

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

