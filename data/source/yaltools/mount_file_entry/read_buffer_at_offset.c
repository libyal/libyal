/* Reads data at a specific offset
 * Returns the number of bytes read or -1 on error
 */
ssize_t mount_file_entry_read_buffer_at_offset(
         mount_file_entry_t *file_entry,
         void *buffer,
         size_t buffer_size,
         off64_t offset,
         libcerror_error_t **error )
{
	${library_name}_${mount_tool_library_type}_t *${mount_tool_source_type} = NULL;
	static char *function                                                   = "mount_file_entry_read_buffer_at_offset";
	ssize_t read_count                                                      = 0;

	if( file_entry == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file entry.",
		 function );

		return( -1 );
	}
	if( mount_file_system_get_${mount_tool_source_type}_by_index(
	     file_entry->file_system,
	     file_entry->${mount_tool_source_type}_index,
	     &${mount_tool_source_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_source_type}: %d from file system.",
		 function,
		 file_entry->${mount_tool_source_type}_index );

		return( -1 );
	}
	read_count = ${library_name}_${mount_tool_library_type}_read_buffer_at_offset(
	              ${mount_tool_source_type},
	              buffer,
	              buffer_size,
	              offset,
	              error );

	if( read_count < 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_READ_FAILED,
		 "%s: unable to read buffer at offset: %" PRIi64 " (0x%08" PRIx64 ") from ${mount_tool_source_type}: %d.",
		 function,
		 offset,
		 offset,
		 file_entry->${mount_tool_source_type}_index );

		return( -1 );
	}
	return( read_count );
}

