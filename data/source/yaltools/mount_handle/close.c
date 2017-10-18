/* Closes the mount handle
 * Returns the 0 if succesful or -1 on error
 */
int mount_handle_close(
     mount_handle_t *mount_handle,
     libcerror_error_t **error )
{
	${library_name}_file_t *${mount_tool_source_type} = NULL;
	static char *function = "mount_handle_close";
	int ${mount_tool_source_type}_index       = 0;
	int number_of_${mount_tool_source_type}s  = 0;

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
	if( libcdata_array_get_number_of_entries(
	     mount_handle->${mount_tool_source_type}s_array,
	     &number_of_${mount_tool_source_type}s,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of ${mount_tool_source_type}s.",
		 function );

		return( -1 );
	}
	for( ${mount_tool_source_type}_index = number_of_${mount_tool_source_type}s - 1;
	     ${mount_tool_source_type}_index > 0;
	     ${mount_tool_source_type}_index-- )
	{
		if( libcdata_array_get_entry_by_index(
		     mount_handle->${mount_tool_source_type}s_array,
		     ${mount_tool_source_type}_index,
		     (intptr_t **) &${mount_tool_source_type},
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve ${mount_tool_source_type}: %d.",
			 function,
			 ${mount_tool_source_type}_index );

			return( -1 );
		}
		if( ${library_name}_file_close(
		     ${mount_tool_source_type},
		     error ) != 0 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_IO,
			 LIBCERROR_IO_ERROR_CLOSE_FAILED,
			 "%s: unable to close ${mount_tool_source_type}: %d.",
			 function,
			 ${mount_tool_source_type}_index );

			return( -1 );
		}
	}
	return( 0 );
}

