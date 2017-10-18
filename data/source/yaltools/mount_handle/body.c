/* Retrieves the media size of a specific ${mount_tool_source_type}
 * Returns 1 if successful or -1 on error
 */
int mount_handle_get_media_size(
     mount_handle_t *mount_handle,
     int ${mount_tool_source_type}_index,
     size64_t *size,
     libcerror_error_t **error )
{
	${library_name}_file_t *${mount_tool_source_type} = NULL;
	static char *function = "mount_handle_get_media_size";

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
	if( libcdata_array_get_entry_by_index(
	     mount_handle->${mount_tool_source_type}s_array,
	     ${mount_tool_source_type}_index,
	     (intptr_t **) &${mount_tool_source_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_source_type}: %d.",
		 function,
		 ${mount_tool_source_type}_index );

		return( -1 );
	}
	if( ${library_name}_file_get_media_size(
	     ${mount_tool_source_type},
	     size,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve media size from ${mount_tool_source_type}: %d.",
		 function,
		 ${mount_tool_source_type}_index );

		return( -1 );
	}
	return( 1 );
}

/* Retrieves the number of ${mount_tool_source_type}s
 * Returns 1 if successful or -1 on error
 */
int mount_handle_get_number_of_${mount_tool_source_type}s(
     mount_handle_t *mount_handle,
     int *number_of_${mount_tool_source_type}s,
     libcerror_error_t **error )
{
	static char *function = "mount_handle_get_number_of_${mount_tool_source_type}s";

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
	if( libcdata_array_get_number_of_entries(
	     mount_handle->${mount_tool_source_type}s_array,
	     number_of_${mount_tool_source_type}s,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of ${mount_tool_source_type}s.",
		 function );

		return( -1 );
	}
	return( 1 );
}

