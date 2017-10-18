/* Sets the basename
 * Returns 1 if successful or -1 on error
 */
int mount_handle_set_basename(
     mount_handle_t *mount_handle,
     const system_character_t *basename,
     size_t basename_size,
     libcerror_error_t **error )
{
	static char *function = "mount_handle_set_basename";

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( basename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid basename.",
		 function );

		return( -1 );
	}
	if( basename_size == 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
		 "%s: missing basename.",
		 function );

		goto on_error;
	}
	if( ( basename_size > (size_t) SSIZE_MAX )
	 || ( ( sizeof( system_character_t ) * basename_size ) > (size_t) SSIZE_MAX ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid basename size value exceeds maximum.",
		 function );

		goto on_error;
	}
	if( mount_handle->basename != NULL )
	{
		memory_free(
		 mount_handle->basename );

		mount_handle->basename      = NULL;
		mount_handle->basename_size = 0;
	}
	mount_handle->basename = system_string_allocate(
	                          basename_size );

	if( mount_handle->basename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create basename string.",
		 function );

		goto on_error;
	}
	if( system_string_copy(
	     mount_handle->basename,
	     basename,
	     basename_size ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_COPY_FAILED,
		 "%s: unable to copy basename.",
		 function );

		goto on_error;
	}
	mount_handle->basename[ basename_size - 1 ] = 0;

	mount_handle->basename_size = basename_size;

	return( 1 );

on_error:
	if( mount_handle->basename != NULL )
	{
		memory_free(
		 mount_handle->basename );

		mount_handle->basename = NULL;
	}
	mount_handle->basename_size = 0;

	return( -1 );
}

