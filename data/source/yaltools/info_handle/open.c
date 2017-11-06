/* Opens the info handle
 * Returns 1 if successful or -1 on error
 */
int info_handle_open(
     info_handle_t *info_handle,
     const system_character_t *filename,
     libcerror_error_t **error )
{
	static char *function = "info_handle_open";

	if( info_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid info handle.",
		 function );

		return( -1 );
	}
	if( ${library_name}_${info_tool_source_type}_set_ascii_codepage(
	     info_handle->${info_tool_source_type},
	     info_handle->ascii_codepage,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set ASCII codepage in ${info_tool_source_type}.",
		 function );

		return( -1 );
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	if( ${library_name}_${info_tool_source_type}_open_wide(
	     info_handle->${info_tool_source_type},
	     filename,
	     ${library_name_upper_case}_OPEN_READ,
	     error ) != 1 )
#else
	if( ${library_name}_${info_tool_source_type}_open(
	     info_handle->${info_tool_source_type},
	     filename,
	     ${library_name_upper_case}_OPEN_READ,
	     error ) != 1 )
#endif
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open ${info_tool_source_type}.",
		 function );

		return( -1 );
	}
	return( 1 );
}

