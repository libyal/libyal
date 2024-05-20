#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )

/* Opens a directory
 * Returns 0 if successful or an error code otherwise
 */
int __stdcall mount_dokan_OpenDirectory(
               const wchar_t *path,
               DOKAN_FILE_INFO *file_info )
{
	libcerror_error_t *error = NULL;
	static char *function    = "mount_dokan_OpenDirectory";
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
	if( file_info->Context != (ULONG64) NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_ALREADY_SET,
		 "%s: invalid file information - context already set.",
		 function );

		result = MOUNT_DOKAN_ERROR_BAD_ARGUMENTS;

		goto on_error;
	}
	if( mount_handle_get_file_entry_by_path(
	     ${mount_tool_name}_mount_handle,
	     path,
	     (mount_file_entry_t **) &( file_info->Context ),
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve file entry for path: %ls.",
		 function,
		 path );

		result = MOUNT_DOKAN_ERROR_FILE_NOT_FOUND;

		goto on_error;
	}
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

#endif /* ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 ) */

