/* Retrieves the access date and time
 * On Windows the timestamp is an unsigned 64-bit FILETIME timestamp
 * otherwise the timestamp is a signed 64-bit POSIX date and time value in number of nanoseconds
 * Returns 1 if successful or -1 on error
 */
int mount_file_entry_get_access_time(
     mount_file_entry_t *file_entry,
     uint64_t *access_time,
     libcerror_error_t **error )
{
	static char *function = "mount_file_entry_get_access_time";
	int64_t posix_time    = 0;

#if defined( WINAPI )
	uint64_t filetime     = 0;
#endif

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
	if( access_time == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid access time.",
		 function );

		return( -1 );
	}
	if( ${library_name}_${mount_tool_file_entry_type}_get_${mount_tool_file_entry_access_time_value}(
	     file_entry->${mount_tool_file_entry_type_name},
	     &posix_time,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_entry_access_time_value_description} from ${mount_tool_file_entry_type_description}.",
		 function );

		return( -1 );
	}
#if defined( WINAPI )
	if( posix_time != 0 )
	{
		/* Convert the POSIX nanoseconds timestamp into a FILETIME timestamp
		 */
		filetime = (uint64_t) ( ( posix_time / 100 ) + 116444736000000000L );
	}
	*access_time = filetime;
#else
	*access_time = (uint64_t) posix_time;
#endif
	return( 1 );
}

