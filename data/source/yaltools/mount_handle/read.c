/* Read a buffer from a specific ${mount_tool_source_type}
 * Returns the number of bytes read if successful or -1 on error
 */
ssize_t mount_handle_read_buffer(
         mount_handle_t *mount_handle,
         int ${mount_tool_source_type}_index,
         uint8_t *buffer,
         size_t size,
         libcerror_error_t **error )
{
	${library_name}_file_t *${mount_tool_source_type} = NULL;
	static char *function = "mount_handle_read_buffer";
	ssize_t read_count    = 0;

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
	read_count = ${library_name}_file_read_buffer(
	              ${mount_tool_source_type},
	              buffer,
	              size,
	              error );

	if( read_count == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_READ_FAILED,
		 "%s: unable to read buffer from ${mount_tool_source_type}: %d.",
		 function,
		 ${mount_tool_source_type}_index );

		return( -1 );
	}
	return( read_count );
}

