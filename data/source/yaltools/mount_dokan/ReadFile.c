/* Reads a buffer of data at the specified offset
 * Returns 0 if successful or an error code otherwise
 */
#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_ReadFile(
               const wchar_t *path,
               void *buffer,
               DWORD number_of_bytes_to_read,
               DWORD *number_of_bytes_read,
               LONGLONG offset,
               DOKAN_FILE_INFO *file_info )
#else
NTSTATUS __stdcall mount_dokan_ReadFile(
                    const wchar_t *path,
                    void *buffer,
                    DWORD number_of_bytes_to_read,
                    DWORD *number_of_bytes_read,
                    LONGLONG offset,
                    DOKAN_FILE_INFO *file_info )
#endif
{
	libcerror_error_t *error = NULL;
	static char *function    = "mount_dokan_ReadFile";
	ssize_t read_count       = 0;
	int result               = 0;

#if defined( HAVE_DEBUG_OUTPUT )
	if( libcnotify_verbose != 0 )
	{
		libcnotify_printf(
		 "%s: %ls\n",
		 function,
		 path );
	}
#endif
	if( path == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid path.",
		 function );

		result = MOUNT_DOKAN_ERROR_BAD_ARGUMENTS;

		goto on_error;
	}
	if( number_of_bytes_to_read > (DWORD) INT32_MAX )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid number of bytes to read value exceeds maximum.",
		 function );

		result = MOUNT_DOKAN_ERROR_BAD_ARGUMENTS;

		goto on_error;
	}
	if( number_of_bytes_read == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid number of bytes read.",
		 function );

		result = MOUNT_DOKAN_ERROR_BAD_ARGUMENTS;

		goto on_error;
	}
	if( file_info == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file information.",
		 function );

		result = MOUNT_DOKAN_ERROR_BAD_ARGUMENTS;

		goto on_error;
	}
	if( file_info->Context == (ULONG64) NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
		 "%s: invalid file information - missing context.",
		 function );

		result = MOUNT_DOKAN_ERROR_BAD_ARGUMENTS;

		goto on_error;
	}
	read_count = mount_file_entry_read_buffer_at_offset(
	              (mount_file_entry_t *) file_info->Context,
	              buffer,
	              (size_t) number_of_bytes_to_read,
	              (off64_t) offset,
	              &error );

	if( read_count < 0 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_READ_FAILED,
		 "%s: unable to read from file entry.",
		 function );

		result = MOUNT_DOKAN_ERROR_READ_FAULT;

		goto on_error;
	}
	if( read_count > (size_t) INT32_MAX )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid read count value exceeds maximum.",
		 function );

		result = MOUNT_DOKAN_ERROR_READ_FAULT;

		goto on_error;
	}
	/* Dokan does not require the read function to return ERROR_HANDLE_EOF
	 */
	*number_of_bytes_read = (DWORD) read_count;

	return( 0 );

on_error:
	if( error != NULL )
	{
		libcnotify_print_error_backtrace(
		 error );
		libcerror_error_free(
		 &error );
	}
	return( result );
}

