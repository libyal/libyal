/* TODO add support for ${mount_tool_file_system_type_description} selection including all ${mount_tool_file_system_type_description}s */
	if( ${library_name}_${mount_tool_base_type}_get_number_of_${mount_tool_file_system_type}s(
	     ${mount_tool_base_type_name},
	     &number_of_${mount_tool_file_system_type}s,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of ${mount_tool_file_system_type_description}s from ${mount_tool_base_type_description}.",
		 function );

		return( -1 );
	}
	${mount_tool_file_system_type}_index = mount_handle->file_system_index;

	if( ( ${mount_tool_file_system_type}_index == 0 )
	 && ( number_of_${mount_tool_file_system_type}s == 1 ) )
	{
		${mount_tool_file_system_type}_index = 1;
	}
	if( ( ${mount_tool_file_system_type}_index <= 0 )
	 || ( ${mount_tool_file_system_type}_index > number_of_${mount_tool_file_system_type}s ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid ${mount_tool_file_system_type_description} index value out of bounds.",
		 function );

		return( -1 );
	}
	${mount_tool_file_system_type}_index -= 1;

	if( mount_handle_get_${mount_tool_file_system_type}_by_index(
	     mount_handle,
	     ${mount_tool_file_system_type}_index,
	     &${mount_tool_file_system_type_name},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_system_type_description}: %d.",
		 function,
		 ${mount_tool_file_system_type}_index );

		return( -1 );
	}
