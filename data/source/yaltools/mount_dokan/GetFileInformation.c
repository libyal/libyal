/* Retrieves the file information
 * Returns 0 if successful or an error code otherwise
 */
#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_GetFileInformation(
               const wchar_t *path,
               BY_HANDLE_FILE_INFORMATION *file_information,
               DOKAN_FILE_INFO *file_info ${tools_name:upper_case}_ATTRIBUTE_UNUSED )
#else
NTSTATUS __stdcall mount_dokan_GetFileInformation(
                    const wchar_t *path,
                    BY_HANDLE_FILE_INFORMATION *file_information,
                    DOKAN_FILE_INFO *file_info ${tools_name:upper_case}_ATTRIBUTE_UNUSED )
#endif
{
	libcerror_error_t *error       = NULL;
	mount_file_entry_t *file_entry = NULL;
	static char *function          = "mount_dokan_GetFileInformation";
	size64_t file_size             = 0;
	uint64_t access_time           = 0;
	uint64_t creation_time         = 0;
	uint64_t modification_time     = 0;
	uint16_t file_mode             = 0;
	int result                     = 0;

	${tools_name:upper_case}_UNREFERENCED_PARAMETER( file_info )

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
	if( mount_handle_get_file_entry_by_path(
	     ${mount_tool_name}_mount_handle,
	     path,
	     &file_entry,
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
	if( file_entry != NULL )
	{
		if( mount_file_entry_get_size(
		     file_entry,
		     &file_size,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve file entry size.",
			 function );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
		if( mount_file_entry_get_file_mode(
		     file_entry,
		     &file_mode,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve file mode.",
			 function );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
		if( mount_file_entry_get_creation_time(
		     file_entry,
		     &creation_time,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve creation time.",
			 function );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
		if( mount_file_entry_get_access_time(
		     file_entry,
		     &access_time,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve access time.",
			 function );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
		if( mount_file_entry_get_modification_time(
		     file_entry,
		     &modification_time,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve modification time.",
			 function );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
	}
	if( mount_dokan_set_file_information(
	     file_information,
	     file_size,
	     file_mode,
	     creation_time,
	     access_time,
	     modification_time,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set file information.",
		 function );

		result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

		goto on_error;
	}
	if( mount_file_entry_free(
	     &file_entry,
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
	return( 0 );

on_error:
	if( error != NULL )
	{
		libcnotify_print_error_backtrace(
		 error );
		libcerror_error_free(
		 &error );
	}
	if( file_entry != NULL )
	{
		mount_file_entry_free(
		 &file_entry,
		 NULL );
	}
	return( result );
}

