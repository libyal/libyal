#elif defined( HAVE_LIBDOKAN )

static wchar_t *${mount_tool_name}_dokan_path_prefix      = L"\\${library_name_suffix_upper_case}";
static size_t ${mount_tool_name}_dokan_path_prefix_length = 5;

/* Opens a file or directory
 * Returns 0 if successful or a negative error code otherwise
 */
int __stdcall ${mount_tool_name}_dokan_CreateFile(
               const wchar_t *path,
               DWORD desired_access,
               DWORD share_mode ${tools_name_upper_case}_ATTRIBUTE_UNUSED,
               DWORD creation_disposition,
               DWORD attribute_flags ${tools_name_upper_case}_ATTRIBUTE_UNUSED,
               DOKAN_FILE_INFO *file_info )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${mount_tool_name}_dokan_CreateFile";
	size_t path_length       = 0;
	int result               = 0;

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( share_mode )
	${tools_name_upper_case}_UNREFERENCED_PARAMETER( attribute_flags )

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
		 "%s: invalid file info.",
		 function );

		result = -ERROR_BAD_ARGUMENTS;

		goto on_error;
	}
	path_length = wide_string_length(
	               path );

	if( path_length == 1 )
	{
		if( path[ 0 ] != (wchar_t) '\\' )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
			 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
			 "%s: unsupported path: %ls.",
			 function,
			 path );

			result = -ERROR_FILE_NOT_FOUND;

			goto on_error;
		}
	}
	else
	{
		if( ( path_length <= ${mount_tool_name}_dokan_path_prefix_length )
		 || ( path_length > ( ${mount_tool_name}_dokan_path_prefix_length + 3 ) )
		 || ( wide_string_compare(
		       path,
		       ${mount_tool_name}_dokan_path_prefix,
		       ${mount_tool_name}_dokan_path_prefix_length ) != 0 ) )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
			 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
			 "%s: unsupported path: %ls.",
			 function,
			 path );

			result = -ERROR_FILE_NOT_FOUND;

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

/* Opens a directory
 * Returns 0 if successful or a negative error code otherwise
 */
int __stdcall ${mount_tool_name}_dokan_OpenDirectory(
               const wchar_t *path,
               DOKAN_FILE_INFO *file_info ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${mount_tool_name}_dokan_OpenDirectory";
	size_t path_length       = 0;
	int result               = 0;

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( file_info )

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
	path_length = wide_string_length(
	               path );

	if( ( path_length != 1 )
	 || ( path[ 0 ] != (wchar_t) '\\' ) )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported path: %ls.",
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

/* Closes a file or direcotry
 * Returns 0 if successful or a negative error code otherwise
 */
int __stdcall ${mount_tool_name}_dokan_CloseFile(
               const wchar_t *path,
               DOKAN_FILE_INFO *file_info ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${mount_tool_name}_dokan_CloseFile";
	int result               = 0;

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( file_info )

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

/* Reads a buffer of data at the specified offset
 * Returns 0 if successful or a negative error code otherwise
 */
int __stdcall ${mount_tool_name}_dokan_ReadFile(
               const wchar_t *path,
               void *buffer,
               DWORD number_of_bytes_to_read,
               DWORD *number_of_bytes_read,
               LONGLONG offset,
               DOKAN_FILE_INFO *file_info ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${mount_tool_name}_dokan_ReadFile";
	size_t path_length       = 0;
	ssize_t read_count       = 0;
	int input_file_index     = 0;
	int result               = 0;
	int string_index         = 0;

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( file_info )

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
	if( number_of_bytes_to_read > (DWORD) INT32_MAX )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid number of bytes to read value exceeds maximum.",
		 function );

		result = -ERROR_BAD_ARGUMENTS;

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

		result = -ERROR_BAD_ARGUMENTS;

		goto on_error;
	}
	path_length = wide_string_length(
	               path );

	if( ( path_length <= ${mount_tool_name}_dokan_path_prefix_length )
         || ( path_length > ( ${mount_tool_name}_dokan_path_prefix_length + 3 ) )
	 || ( wide_string_compare(
	       path,
	       ${mount_tool_name}_dokan_path_prefix,
	       ${mount_tool_name}_dokan_path_prefix_length ) != 0 ) )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported path: %ls.",
		 function,
		 path );

		result = -ERROR_FILE_NOT_FOUND;

		goto on_error;
	}
	string_index = (int) ${mount_tool_name}_dokan_path_prefix_length;

	input_file_index = path[ string_index++ ] - (wchar_t) '0';

	if( string_index < (int) path_length )
	{
		input_file_index *= 10;
		input_file_index += path[ string_index++ ] - (wchar_t) '0';
	}
	if( string_index < (int) path_length )
	{
		input_file_index *= 10;
		input_file_index += path[ string_index++ ] - (wchar_t) '0';
	}
	input_file_index -= 1;

	if( mount_handle_seek_offset(
	     ${mount_tool_name}_mount_handle,
	     input_file_index,
	     (off64_t) offset,
	     SEEK_SET,
	     &error ) == -1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_SEEK_FAILED,
		 "%s: unable to seek offset in mount handle.",
		 function );

		result = -ERROR_SEEK_ON_DEVICE;

		goto on_error;
	}
	read_count = mount_handle_read_buffer(
		      ${mount_tool_name}_mount_handle,
		      input_file_index,
		      (uint8_t *) buffer,
		      (size_t) number_of_bytes_to_read,
		      &error );

	if( read_count == -1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_READ_FAILED,
		 "%s: unable to read from mount handle.",
		 function );

		result = -ERROR_READ_FAULT;

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

		result = -ERROR_READ_FAULT;

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

/* Sets the values in a find data structure
 * Returns 1 if successful or -1 on error
 */
int ${mount_tool_name}_dokan_set_find_data(
     WIN32_FIND_DATAW *find_data,
     size64_t size,
     int number_of_sub_items,
     uint8_t use_mount_time,
     libcerror_error_t **error )
{
	static char *function = "${mount_tool_name}_dokan_set_find_data";

	if( find_data == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid find data.",
		 function );

		return( -1 );
	}
/* TODO implement
	if( use_mount_time != 0 )
	{
	}
*/
	if( size > 0 )
	{
		find_data->nFileSizeHigh = (DWORD) ( size >> 32 );
		find_data->nFileSizeLow  = (DWORD) ( size & 0xffffffffUL );
	}
	find_data->dwFileAttributes = FILE_ATTRIBUTE_READONLY;

	if( number_of_sub_items > 0 )
	{
		find_data->dwFileAttributes |= FILE_ATTRIBUTE_DIRECTORY;
	}
	return( 1 );
}

/* Fills a directory entry
 * Returns 1 if successful or -1 on error
 */
int ${mount_tool_name}_dokan_filldir(
     PFillFindData fill_find_data,
     DOKAN_FILE_INFO *file_info,
     wchar_t *name,
     size_t name_size,
     WIN32_FIND_DATAW *find_data,
     mount_handle_t *mount_handle,
     int input_file_index,
     uint8_t use_mount_time,
     libcerror_error_t **error )
{
	static char *function   = "${mount_tool_name}_dokan_filldir";
	size64_t media_size     = 0;
	int number_of_sub_items = 0;

	if( fill_find_data == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid fill find data.",
		 function );

		return( -1 );
	}
	if( name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid name.",
		 function );

		return( -1 );
	}
	if( name_size > (size_t) MAX_PATH )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid name size value out of bounds.",
		 function );

		return( -1 );
	}
	if( mount_handle == NULL )
	{
		number_of_sub_items = 1;
	}
	else
	{
		if( mount_handle_get_media_size(
		     mount_handle,
		     input_file_index,
		     &media_size,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve media size.",
			 function );

			return( -1 );
		}
	}
	if( memory_set(
	     find_data,
	     0,
	     sizeof( WIN32_FIND_DATAW ) ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to clear find data.",
		 function );

		return( -1 );
	}
	if( wide_string_copy(
	     find_data->cFileName,
	     name,
	     name_size ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_COPY_FAILED,
		 "%s: unable to copy filename.",
		 function );

		return( -1 );
	}
	if( name_size <= (size_t) 14 )
	{
		if( wide_string_copy(
		     find_data->cAlternateFileName,
		     name,
		     name_size ) == NULL )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_MEMORY,
			 LIBCERROR_MEMORY_ERROR_COPY_FAILED,
			 "%s: unable to copy alternate filename.",
			 function );

			return( -1 );
		}
	}
	if( ${mount_tool_name}_dokan_set_find_data(
	     find_data,
	     media_size,
	     number_of_sub_items,
	     use_mount_time,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set find data.",
		 function );

		return( -1 );
	}
	if( fill_find_data(
	     find_data,
	     file_info ) != 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set directory entry.",
		 function );

		return( -1 );
	}
	return( 1 );
}

/* Reads a directory
 * Returns 0 if successful or a negative error code otherwise
 */
int __stdcall ${mount_tool_name}_dokan_FindFiles(
               const wchar_t *path,
               PFillFindData fill_find_data,
               DOKAN_FILE_INFO *file_info )
{
	WIN32_FIND_DATAW find_data;

	wchar_t ${mount_tool_name}_dokan_path[ 10 ];

	libcerror_error_t *error  = NULL;
	static char *function     = "${mount_tool_name}_dokan_FindFiles";
	size_t path_length        = 0;
	int input_file_index      = 0;
	int number_of_input_files = 0;
	int result                = 0;
	int string_index          = 0;

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
	path_length = wide_string_length(
	               path );

	if( ( path_length != 1 )
	 || ( path[ 0 ] != (wchar_t) '\\' ) )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported path: %ls.",
		 function,
		 path );

		result = -ERROR_FILE_NOT_FOUND;

		goto on_error;
	}
	if( wide_string_copy(
	     ${mount_tool_name}_dokan_path,
	     ${mount_tool_name}_dokan_path_prefix,
	     ${mount_tool_name}_dokan_path_prefix_length ) == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_COPY_FAILED,
		 "%s: unable to copy path prefix.",
		 function );

		result = -ERROR_GEN_FAILURE;

		goto on_error;
	}
	if( mount_handle_get_number_of_input_files(
	     ${mount_tool_name}_mount_handle,
	     &number_of_input_files,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of input files.",
		 function );

		result = -ERROR_GEN_FAILURE;

		goto on_error;
	}
	if( ( number_of_input_files < 0 )
	 || ( number_of_input_files > 99 ) )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported number of input files.",
		 function );

		result = -ERROR_GEN_FAILURE;

		goto on_error;
	}
	if( ${mount_tool_name}_dokan_filldir(
	     fill_find_data,
	     file_info,
	     L".",
	     2,
	     &find_data,
	     NULL,
	     -1,
	     1,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set find data.",
		 function );

		result = -ERROR_GEN_FAILURE;

		goto on_error;
	}
	if( ${mount_tool_name}_dokan_filldir(
	     fill_find_data,
	     file_info,
	     L"..",
	     3,
	     &find_data,
	     NULL,
	     -1,
	     0,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set find data.",
		 function );

		result = -ERROR_GEN_FAILURE;

		goto on_error;
	}
	for( input_file_index = 1;
	     input_file_index <= number_of_input_files;
	     input_file_index++ )
	{
		string_index = (int) ${mount_tool_name}_dokan_path_prefix_length;

		if( input_file_index >= 100 )
		{
			${mount_tool_name}_dokan_path[ string_index++ ] = (wchar_t) ( '0' + ( input_file_index / 100 ) );
		}
		if( input_file_index >= 10 )
		{
			${mount_tool_name}_dokan_path[ string_index++ ] = (wchar_t) ( '0' + ( input_file_index / 10 ) );
		}
		${mount_tool_name}_dokan_path[ string_index++ ] = (wchar_t) ( '0' + ( input_file_index % 10 ) );
		${mount_tool_name}_dokan_path[ string_index++ ] = 0;

/* TODO add support for multiple input files ? */
		if( input_file_index != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
			 "%s: invalid input file index value out of bounds.",
			 function );

			result = -ERROR_BAD_ARGUMENTS;

			goto on_error;
		}
		if( ${mount_tool_name}_dokan_filldir(
		     fill_find_data,
		     file_info,
		     &( ${mount_tool_name}_dokan_path[ 1 ] ),
		     string_index - 1,
		     &find_data,
		     ${mount_tool_name}_mount_handle,
		     input_file_index - 1,
		     1,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to set find data.",
			 function );

			result = -ERROR_GEN_FAILURE;

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

/* Sets the values in a file information structure
 * Returns 1 if successful or -1 on error
 */
int ${mount_tool_name}_dokan_set_file_information(
     BY_HANDLE_FILE_INFORMATION *file_information,
     size64_t size,
     int number_of_sub_items,
     uint8_t use_mount_time,
     libcerror_error_t **error )
{
	static char *function = "${mount_tool_name}_dokan_set_file_information";

	if( file_information == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file information.",
		 function );

		return( -1 );
	}
/* TODO implement
	if( use_mount_time != 0 )
	{
	}
*/
	if( size > 0 )
	{
		file_information->nFileSizeHigh = (DWORD) ( size >> 32 );
		file_information->nFileSizeLow  = (DWORD) ( size & 0xffffffffUL );
	}
	file_information->dwFileAttributes = FILE_ATTRIBUTE_READONLY;

	if( number_of_sub_items > 0 )
	{
		file_information->dwFileAttributes |= FILE_ATTRIBUTE_DIRECTORY;
	}
	return( 1 );
}

/* Retrieves the file information
 * Returns 0 if successful or a negative error code otherwise
 */
int __stdcall ${mount_tool_name}_dokan_GetFileInformation(
               const wchar_t *path,
               BY_HANDLE_FILE_INFORMATION *file_information,
               DOKAN_FILE_INFO *file_info )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${mount_tool_name}_dokan_GetFileInformation";
	size64_t media_size      = 0;
	size_t path_length       = 0;
	int input_file_index     = 0;
	int number_of_sub_items  = 0;
	int result               = 0;
	int string_index         = 0;
	uint8_t use_mount_time   = 0;

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
	if( file_info == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file info.",
		 function );

		result = -ERROR_BAD_ARGUMENTS;

		goto on_error;
	}
	path_length = wide_string_length(
	               path );

	if( path_length == 1 )
	{
		if( path[ 0 ] != (wchar_t) '\\' )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
			 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
			 "%s: unsupported path: %ls.",
			 function,
			 path );

			result = -ERROR_FILE_NOT_FOUND;

			goto on_error;
		}
		number_of_sub_items = 1;
		use_mount_time      = 1;
	}
	else
	{
		if( ( path_length <= ${mount_tool_name}_dokan_path_prefix_length )
		 || ( path_length > ( ${mount_tool_name}_dokan_path_prefix_length + 3 ) )
		 || ( wide_string_compare(
		       path,
		       ${mount_tool_name}_dokan_path_prefix,
		       ${mount_tool_name}_dokan_path_prefix_length ) != 0 ) )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
			 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
			 "%s: unsupported path: %ls.",
			 function,
			 path );

			result = -ERROR_FILE_NOT_FOUND;

			goto on_error;
		}
		string_index = (int) ${mount_tool_name}_dokan_path_prefix_length;

		input_file_index = path[ string_index++ ] - (wchar_t) '0';

		if( string_index < (int) path_length )
		{
			input_file_index *= 10;
			input_file_index += path[ string_index++ ] - (wchar_t) '0';
		}
		if( string_index < (int) path_length )
		{
			input_file_index *= 10;
			input_file_index += path[ string_index++ ] - (wchar_t) '0';
		}
		input_file_index -= 1;

/* TODO add support for multiple input files ? */
		if( input_file_index != 0 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
			 "%s: invalid input file index value out of bounds.",
			 function );

			result = -ERROR_BAD_ARGUMENTS;

			goto on_error;
		}
		if( mount_handle_get_media_size(
		     ${mount_tool_name}_mount_handle,
		     input_file_index,
		     &media_size,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve media size.",
			 function );

			result = -ERROR_GEN_FAILURE;

			goto on_error;
		}
		use_mount_time = 1;
	}
	if( ${mount_tool_name}_dokan_set_file_information(
	     file_information,
	     media_size,
	     number_of_sub_items,
	     use_mount_time,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set file info.",
		 function );

		result = -ERROR_GEN_FAILURE;

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

/* Retrieves the volume information
 * Returns 0 if successful or a negative error code otherwise
 */
int __stdcall ${mount_tool_name}_dokan_GetVolumeInformation(
               wchar_t *volume_name,
               DWORD volume_name_size,
               DWORD *volume_serial_number,
               DWORD *maximum_filename_length,
               DWORD *file_system_flags,
               wchar_t *file_system_name,
               DWORD file_system_name_size,
               DOKAN_FILE_INFO *file_info ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${mount_tool_name}_dokan_GetVolumeInformation";
	int result               = 0;

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( file_info )

	if( ( volume_name != NULL )
	 && ( volume_name_size > (DWORD) ( sizeof( wchar_t ) * 5 ) ) )
	{
		/* Using wcsncpy seems to cause strange behavior here
		 */
		if( memory_copy(
		     volume_name,
		     L"${library_name_suffix_upper_case}",
		     sizeof( wchar_t ) * 5 ) == NULL )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_MEMORY,
			 LIBCERROR_MEMORY_ERROR_COPY_FAILED,
			 "%s: unable to copy volume name.",
			 function );

			result = -ERROR_GEN_FAILURE;

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
	if( ( file_system_name != NULL )
	 && ( file_system_name_size > (DWORD) ( sizeof( wchar_t ) * 6 ) ) )
	{
		/* Using wcsncpy seems to cause strange behavior here
		 */
		if( memory_copy(
		     file_system_name,
		     L"Dokan",
		     sizeof( wchar_t ) * 6 ) == NULL )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_MEMORY,
			 LIBCERROR_MEMORY_ERROR_COPY_FAILED,
			 "%s: unable to copy file system name.",
			 function );

			result = -ERROR_GEN_FAILURE;

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

/* Unmount the image
 * Returns 0 if successful or a negative error code otherwise
 */
int __stdcall ${mount_tool_name}_dokan_Unmount(
               DOKAN_FILE_INFO *file_info ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
{
	static char *function = "${mount_tool_name}_dokan_Unmount";

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( file_info )

	return( 0 );
}

