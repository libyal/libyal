	if( mount_file_system_get_number_of_${mount_tool_file_system_type}s(
	     mount_handle->file_system,
	     &number_of_${mount_tool_file_system_type}s,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of ${mount_tool_file_system_type_description}s.",
		 function );

		goto on_error;
	}
	for( ${mount_tool_file_system_type}_index = number_of_${mount_tool_file_system_type}s - 1;
	     ${mount_tool_file_system_type}_index > 0;
	     ${mount_tool_file_system_type}_index-- )
	{
		if( mount_file_system_get_${mount_tool_file_system_type}_by_index(
		     mount_handle->file_system,
		     ${mount_tool_file_system_type}_index,
		     &${mount_tool_file_system_type},
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve ${mount_tool_file_system_type_description}: %d.",
			 function,
			 ${mount_tool_file_system_type}_index );

			goto on_error;
		}
/* TODO remove ${mount_tool_file_system_type} from file system */

		if( ${library_name}_${mount_tool_file_system_type}_close(
		     ${mount_tool_file_system_type},
		     error ) != 0 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_IO,
			 LIBCERROR_IO_ERROR_CLOSE_FAILED,
			 "%s: unable to close ${mount_tool_file_system_type_description}: %d.",
			 function,
			 ${mount_tool_file_system_type}_index );

			goto on_error;
		}
		if( ${library_name}_${mount_tool_file_system_type}_free(
		     &${mount_tool_file_system_type},
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
			 "%s: unable to free ${mount_tool_file_system_type_description}: %d.",
			 function,
			 ${mount_tool_file_system_type}_index );

			goto on_error;
		}
	}
