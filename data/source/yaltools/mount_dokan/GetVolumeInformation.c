/* Retrieves the volume information
 * Returns 0 if successful or an error code otherwise
 */
#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_GetVolumeInformation(
               wchar_t *volume_name,
               DWORD volume_name_size,
               DWORD *volume_serial_number,
               DWORD *maximum_filename_length,
               DWORD *file_system_flags,
               wchar_t *file_system_name,
               DWORD file_system_name_size,
               DOKAN_FILE_INFO *file_info ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
#else
NTSTATUS __stdcall mount_dokan_GetVolumeInformation(
                    wchar_t *volume_name,
                    DWORD volume_name_size,
                    DWORD *volume_serial_number,
                    DWORD *maximum_filename_length,
                    DWORD *file_system_flags,
                    wchar_t *file_system_name,
                    DWORD file_system_name_size,
                    DOKAN_FILE_INFO *file_info ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
#endif
{
	libcerror_error_t *error = NULL;
	const wchar_t *name      = NULL;
	static char *function    = "mount_dokan_GetVolumeInformation";
	size_t name_size         = 0;
	int result               = 0;

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( file_info )

#if defined( HAVE_DEBUG_OUTPUT )
	if( libcnotify_verbose != 0 )
	{
		libcnotify_printf(
		 "%s: %ls\n",
		 function,
		 volume_name );
	}
#endif
	name      = L"${library_name_suffix_upper_case}";
	name_size = 1 + wide_string_length(
	                 name );

	if( ( volume_name != NULL )
	 && ( volume_name_size > (DWORD) name_size ) )
	{
		/* Using wcsncpy seems to cause strange behavior here
		 */
		if( memory_copy(
		     volume_name,
		     name,
		     name_size * sizeof( wchar_t ) ) == NULL )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_MEMORY,
			 LIBCERROR_MEMORY_ERROR_COPY_FAILED,
			 "%s: unable to copy volume name.",
			 function );

			result = MOUNT_DOKAN_ERROR_GENERIC_FAILURE;

			goto on_error;
		}
	}
	if( volume_serial_number != NULL )
	{
		/* If this value contains 0 it can crash the system is this an issue in Dokan?
		 */
		*volume_serial_number = 0x19831116;
	}
	if( maximum_filename_length != NULL )
	{
		*maximum_filename_length = 256;
	}
	if( file_system_flags != NULL )
	{
		*file_system_flags = FILE_CASE_SENSITIVE_SEARCH
		                   | FILE_CASE_PRESERVED_NAMES
		                   | FILE_UNICODE_ON_DISK
		                   | FILE_READ_ONLY_VOLUME;
	}
	name      = L"Dokan";
	name_size = 1 + wide_string_length(
	                 name );

	if( ( file_system_name != NULL )
	 && ( file_system_name_size > (DWORD) name_size ) )
	{
		/* Using wcsncpy seems to cause strange behavior here
		 */
		if( memory_copy(
		     file_system_name,
		     name,
		     name_size * sizeof( wchar_t ) ) == NULL )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_MEMORY,
			 LIBCERROR_MEMORY_ERROR_COPY_FAILED,
			 "%s: unable to copy file system name.",
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

