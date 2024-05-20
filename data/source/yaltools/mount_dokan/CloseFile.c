/* Closes a file or directory
 * Returns 0 if successful or an error code otherwise
 */
#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_CloseFile(
               const wchar_t *path,
               DOKAN_FILE_INFO *file_info )
#else
NTSTATUS __stdcall mount_dokan_CloseFile(
                    const wchar_t *path,
                    DOKAN_FILE_INFO *file_info )
#endif
{
	libcerror_error_t *error = NULL;
	static char *function    = "mount_dokan_CloseFile";
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
		if( mount_file_entry_free(
		     (mount_file_entry_t **) &( file_info->Context ),
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
			 "%s: unable to free file entry.",
			 function );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
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

