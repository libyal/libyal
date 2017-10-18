/* Seeks a specific offset in a specific ${mount_tool_source_type}
 * Returns the offset if successful or -1 on error
 */
off64_t mount_handle_seek_offset(
         mount_handle_t *mount_handle,
         int ${mount_tool_source_type}_index,
         off64_t offset,
         int whence,
         libcerror_error_t **error )
{
	${library_name}_file_t *${mount_tool_source_type} = NULL;
	static char *function = "mount_handle_seek_offset";

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
	offset = ${library_name}_file_seek_offset(
	          ${mount_tool_source_type},
	          offset,
	          whence,
	          error );

	if( offset == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_SEEK_FAILED,
		 "%s: unable to seek offset in ${mount_tool_source_type}: %d.",
		 function,
		 ${mount_tool_source_type}_index );

		return( -1 );
	}
	return( offset );
}

