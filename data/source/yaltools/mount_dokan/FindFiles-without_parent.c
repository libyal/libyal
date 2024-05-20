/* Reads a directory
 * Returns 0 if successful or an error code otherwise
 */
#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_FindFiles(
               const wchar_t *path,
               PFillFindData fill_find_data,
               DOKAN_FILE_INFO *file_info )
#else
NTSTATUS __stdcall mount_dokan_FindFiles(
                    const wchar_t *path,
                    PFillFindData fill_find_data,
                    DOKAN_FILE_INFO *file_info )
#endif
{
	WIN32_FIND_DATAW find_data;

	libcerror_error_t *error           = NULL;
	mount_file_entry_t *file_entry     = NULL;
	mount_file_entry_t *sub_file_entry = NULL;
	wchar_t *name                      = NULL;
	static char *function              = "mount_dokan_FindFiles";
	size_t name_size                   = 0;
	int number_of_sub_file_entries     = 0;
	int result                         = 0;
	int sub_file_entry_index           = 0;

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
	if( mount_dokan_filldir(
	     fill_find_data,
	     file_info,
	     L".",
	     2,
	     &find_data,
	     file_entry,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set self find data.",
		 function );

		result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

		goto on_error;
	}
	if( mount_dokan_filldir(
	     fill_find_data,
	     file_info,
	     L"..",
	     3,
	     &find_data,
	     NULL,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set parent find data.",
		 function );

		result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

		goto on_error;
	}
	if( mount_file_entry_get_number_of_sub_file_entries(
	     file_entry,
	     &number_of_sub_file_entries,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of sub file entries.",
		 function );

		result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

		goto on_error;
	}
	for( sub_file_entry_index = 0;
	     sub_file_entry_index < number_of_sub_file_entries;
	     sub_file_entry_index++ )
	{
		if( mount_file_entry_get_sub_file_entry_by_index(
		     file_entry,
		     sub_file_entry_index,
		     &sub_file_entry,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve sub file entry: %d.",
			 function,
			 sub_file_entry_index );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
		if( mount_file_entry_get_name_size(
		     sub_file_entry,
		     &name_size,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve sub file entry: %d name size.",
			 function,
			 sub_file_entry_index );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
		name = wide_string_allocate(
		        name_size );

		if( name == NULL )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_MEMORY,
			 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
			 "%s: unable to create sub file entry: %d name.",
			 function );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
		if( mount_file_entry_get_name(
		     sub_file_entry,
		     name,
		     name_size,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve sub file entry: %d name.",
			 function,
			 sub_file_entry_index );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
		if( mount_dokan_filldir(
		     fill_find_data,
		     file_info,
		     name,
		     name_size,
		     &find_data,
		     sub_file_entry,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to set sub file entry: %d find data.",
			 function,
			 sub_file_entry_index );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
		memory_free(
		 name );

		name = NULL;

		if( mount_file_entry_free(
		     &sub_file_entry,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
			 "%s: unable to free sub file entry: %d.",
			 function,
			 sub_file_entry_index );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
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
	if( name != NULL )
	{
		memory_free(
		 name );
	}
	if( sub_file_entry != NULL )
	{
		mount_file_entry_free(
		 &sub_file_entry,
		 NULL );
	}
	if( file_entry != NULL )
	{
		mount_file_entry_free(
		 &file_entry,
		 NULL );
	}
	return( result );
}

