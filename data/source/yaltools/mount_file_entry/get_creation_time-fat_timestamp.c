/* Retrieves the creation date and time
 * On Windows the timestamp is an unsigned 64-bit FILETIME timestamp
 * otherwise the timestamp is a signed 64-bit POSIX date and time value in number of nanoseconds
 * Returns 1 if successful or -1 on error
 */
int mount_file_entry_get_creation_time(
     mount_file_entry_t *file_entry,
     uint64_t *creation_time,
     libcerror_error_t **error )
{
	static char *function = "mount_file_entry_get_creation_time";
	uint64_t filetime     = 0;

#if !defined( WINAPI )
	int64_t posix_time    = 0;
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
	if( creation_time == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid creation time.",
		 function );

		return( -1 );
	}
	if( ${library_name}_${mount_tool_file_entry_type}_get_${mount_tool_file_entry_creation_time_value}(
	     file_entry->${mount_tool_file_entry_type_name},
	     &filetime,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_entry_creation_time_value_description} from ${mount_tool_file_entry_type_description}.",
		 function );

		return( -1 );
	}
#if defined( WINAPI )
	*creation_time = filetime;
#else
	if( filetime != 0 )
	{
		/* Convert the FILETIME timestamp into a POSIX nanoseconds timestamp
		 */
		posix_time = ( (int64_t) filetime - 116444736000000000L ) * 100;
	}
	*creation_time = (uint64_t) posix_time;
#endif
	return( 1 );
}

