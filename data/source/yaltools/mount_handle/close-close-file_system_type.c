	if( mount_file_system_get_${mount_tool_file_system_type}(
	     mount_handle->file_system,
	     &${mount_tool_file_system_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_system_type_description} from file system.",
		 function );

		goto on_error;
	}
	if( mount_file_system_set_${mount_tool_file_system_type}(
	     mount_handle->file_system,
	     NULL,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set ${mount_tool_file_system_type_description} in file system.",
		 function );

		${mount_tool_file_system_type} = NULL;

		goto on_error;
	}
	if( ${library_name}_${mount_tool_file_system_type}_close(
	     ${mount_tool_file_system_type},
	     error ) != 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_CLOSE_FAILED,
		 "%s: unable to close ${mount_tool_file_system_type_description}.",
		 function );

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
		 "%s: unable to free ${mount_tool_file_system_type_description}.",
		 function );

		goto on_error;
	}
