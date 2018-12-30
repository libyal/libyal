/* Retrieves the ${mount_tool_file_entry_type_description} of a specific path
 * Returns 1 if successful, 0 if no such ${mount_tool_file_entry_type_description} or -1 on error
 */
int mount_file_system_get_${mount_tool_file_entry_type}_by_path(
     mount_file_system_t *file_system,
     const system_character_t *path,
     size_t path_length,
     ${library_name}_${mount_tool_file_entry_type}_t **${mount_tool_file_entry_type},
     libcerror_error_t **error )
{
	system_character_t *${mount_tool_file_entry_type}_path = NULL;
	static char *function                                  = "mount_file_system_get_${mount_tool_file_entry_type}_by_path";
	size_t ${mount_tool_file_entry_type}_path_length       = 0;
	size_t ${mount_tool_file_entry_type}_path_size         = 0;
	int result                                             = 0;

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
	if( path_length == 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid path length.",
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
	if( path[ 0 ] != LIBCPATH_SEPARATOR )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported path - path is not absolute.",
		 function );

		return( -1 );
	}
	if( mount_file_system_get_${mount_tool_file_entry_type}_path_from_path(
	     file_system,
	     path,
	     path_length,
	     &${mount_tool_file_entry_type}_path,
	     &${mount_tool_file_entry_type}_path_size,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_entry_type_description} path from path.",
		 function );

		goto on_error;
	}
	if( ${mount_tool_file_entry_type}_path == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
		 "%s: missing ${mount_tool_file_entry_type_description} path.",
		 function );

		goto on_error;
	}
	${mount_tool_file_entry_type}_path_length = system_string_length(
	                                             ${mount_tool_file_entry_type}_path );

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_file_get_${mount_tool_file_entry_type}_by_utf16_path(
	          file_system->file,
	          (uint16_t *) ${mount_tool_file_entry_type}_path,
	          ${mount_tool_file_entry_type}_path_length,
	          ${mount_tool_file_entry_type},
	          error );
#else
	result = ${library_name}_file_get_${mount_tool_file_entry_type}_by_utf8_path(
	          file_system->file,
	          (uint8_t *) ${mount_tool_file_entry_type}_path,
	          ${mount_tool_file_entry_type}_path_length,
	          ${mount_tool_file_entry_type},
	          error );
#endif
	if( result == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_entry_type_description} ",
		 function );

		goto on_error;
	}
	memory_free(
	 ${mount_tool_file_entry_type}_path );

	return( result );

on_error:
	if( ${mount_tool_file_entry_type}_path != NULL )
	{
		memory_free(
		 ${mount_tool_file_entry_type}_path );
	}
	return( -1 );
}

