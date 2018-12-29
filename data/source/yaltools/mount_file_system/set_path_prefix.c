/* Sets the path prefix
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_set_path_prefix(
     mount_file_system_t *file_system,
     const system_character_t *path_prefix,
     size_t path_prefix_size,
     libcerror_error_t **error )
{
	static char *function = "mount_file_system_set_path_prefix";

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
	if( file_system->path_prefix != NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_ALREADY_SET,
		 "%s: invalid file system - path prefix value already set.",
		 function );

		return( -1 );
	}
	if( path_prefix == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid path prefix.",
		 function );

		return( -1 );
	}
	if( path_prefix_size == 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
		 "%s: missing path prefix.",
		 function );

		goto on_error;
	}
	if( path_prefix_size > (size_t) ( SSIZE_MAX / sizeof( system_character_t ) ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid path prefix size value exceeds maximum.",
		 function );

		goto on_error;
	}
	file_system->path_prefix = system_string_allocate(
	                            path_prefix_size );

	if( file_system->path_prefix == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create path prefix string.",
		 function );

		goto on_error;
	}
	if( system_string_copy(
	     file_system->path_prefix,
	     path_prefix,
	     path_prefix_size ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_COPY_FAILED,
		 "%s: unable to copy path prefix.",
		 function );

		goto on_error;
	}
	file_system->path_prefix[ path_prefix_size - 1 ] = 0;

	file_system->path_prefix_size = path_prefix_size;

	return( 1 );

on_error:
	if( file_system->path_prefix != NULL )
	{
		memory_free(
		 file_system->path_prefix );

		file_system->path_prefix = NULL;
	}
	file_system->path_prefix_size = 0;

	return( -1 );
}

