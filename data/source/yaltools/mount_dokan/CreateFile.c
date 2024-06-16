#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )

/* Opens a file or directory
 * Returns 0 if successful or an error code otherwise
 */
int __stdcall mount_dokan_CreateFile(
               const wchar_t *path,
               DWORD desired_access,
               DWORD share_mode ${tools_name:upper_case}_ATTRIBUTE_UNUSED,
               DWORD creation_disposition,
               DWORD attribute_flags ${tools_name:upper_case}_ATTRIBUTE_UNUSED,
               DOKAN_FILE_INFO *file_info )
{
	libcerror_error_t *error = NULL;
	static char *function    = "mount_dokan_CreateFile";
	int result               = 0;

	${tools_name:upper_case}_UNREFERENCED_PARAMETER( share_mode )
	${tools_name:upper_case}_UNREFERENCED_PARAMETER( attribute_flags )

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

		result = -ERROR_BAD_ARGUMENTS;

		goto on_error;
	}
	if( ( desired_access & GENERIC_WRITE ) != 0 )
	{
		return( -ERROR_WRITE_PROTECT );
	}
	/* Ignore the share_mode
	 */
	if( creation_disposition == CREATE_NEW )
	{
		return( -ERROR_FILE_EXISTS );
	}
	else if( creation_disposition == CREATE_ALWAYS )
	{
		return( -ERROR_ALREADY_EXISTS );
	}
	else if( creation_disposition == OPEN_ALWAYS )
	{
		return( -ERROR_FILE_NOT_FOUND );
	}
	else if( creation_disposition == TRUNCATE_EXISTING )
	{
		return( -ERROR_FILE_NOT_FOUND );
	}
	else if( creation_disposition != OPEN_EXISTING )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid creation disposition.",
		 function );

		result = -ERROR_BAD_ARGUMENTS;

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

		result = -ERROR_BAD_ARGUMENTS;

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

		result = -ERROR_BAD_ARGUMENTS;

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

		result = -ERROR_FILE_NOT_FOUND;

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

#else

/* Opens a file or directory
 * Returns 0 if successful or an error code otherwise
 */
NTSTATUS __stdcall mount_dokan_ZwCreateFile(
                    const wchar_t *path,
                    DOKAN_IO_SECURITY_CONTEXT *security_context ${tools_name:upper_case}_ATTRIBUTE_UNUSED,
                    ACCESS_MASK desired_access,
                    ULONG file_attributes ${tools_name:upper_case}_ATTRIBUTE_UNUSED,
                    ULONG share_access ${tools_name:upper_case}_ATTRIBUTE_UNUSED,
                    ULONG creation_disposition,
                    ULONG creation_options ${tools_name:upper_case}_ATTRIBUTE_UNUSED,
                    DOKAN_FILE_INFO *file_info )
{
	libcerror_error_t *error = NULL;
	static char *function    = "mount_dokan_ZwCreateFile";
	int result               = 0;

	${tools_name:upper_case}_UNREFERENCED_PARAMETER( security_context )
	${tools_name:upper_case}_UNREFERENCED_PARAMETER( file_attributes )
	${tools_name:upper_case}_UNREFERENCED_PARAMETER( share_access )
	${tools_name:upper_case}_UNREFERENCED_PARAMETER( creation_options )

	if( path == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid path.",
		 function );

		result = STATUS_UNSUCCESSFUL;

		goto on_error;
	}
	if( ( desired_access & GENERIC_WRITE ) != 0 )
	{
		return( STATUS_MEDIA_WRITE_PROTECTED );
	}
	/* Ignore the share_mode
	 */
	if( creation_disposition == FILE_CREATE )
	{
		return( STATUS_OBJECT_NAME_COLLISION );
	}
	else if( ( creation_disposition != FILE_OPEN )
	      && ( creation_disposition != FILE_OPEN_IF ) )
	{
		return( STATUS_ACCESS_DENIED );
	}
	if( file_info == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file information.",
		 function );

		result = STATUS_UNSUCCESSFUL;

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

		result = STATUS_UNSUCCESSFUL;

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

		result = STATUS_OBJECT_NAME_NOT_FOUND;

		goto on_error;
	}
	return( STATUS_SUCCESS );

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

