/* Signals the mount handle to abort
 * Returns 1 if successful or -1 on error
 */
int mount_handle_signal_abort(
     mount_handle_t *mount_handle,
     libcerror_error_t **error )
{
	${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type} = NULL;
	static char *function                                                          = "mount_handle_signal_abort";
	int ${mount_tool_file_entry_type}_index                                        = 0;
	int number_of_${mount_tool_file_entry_type}s                                   = 0;

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( mount_file_system_get_number_of_${mount_tool_file_entry_type}s(
	     mount_handle->file_system,
	     &number_of_${mount_tool_file_entry_type}s,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of ${mount_tool_file_entry_type_description}s.",
		 function );

		return( -1 );
	}
	for( ${mount_tool_file_entry_type}_index = number_of_${mount_tool_file_entry_type}s - 1;
	     ${mount_tool_file_entry_type}_index > 0;
	     ${mount_tool_file_entry_type}_index-- )
	{
		if( mount_file_system_get_${mount_tool_file_entry_type}_by_index(
		     mount_handle->file_system,
		     ${mount_tool_file_entry_type}_index,
		     &${mount_tool_file_entry_type},
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve ${mount_tool_file_entry_type_description}: %d.",
			 function,
			 ${mount_tool_file_entry_type}_index );

			return( -1 );
		}
		if( ${library_name}_${mount_tool_file_entry_type}_signal_abort(
		     ${mount_tool_file_entry_type},
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to signal ${mount_tool_file_entry_type_description}: %d to abort.",
			 function,
			 ${mount_tool_file_entry_type}_index );

			return( -1 );
		}
	}
	return( 1 );
}
