		if( path_length > 1 )
		{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
			result = libolecf_${mount_tool_file_entry_type}_get_utf16_name_size(
			          ${mount_tool_file_entry_type},
			          &${mount_tool_file_entry_type}_name_size,
			          error );
#else
			result = libolecf_${mount_tool_file_entry_type}_get_utf8_name_size(
			          ${mount_tool_file_entry_type},
			          &${mount_tool_file_entry_type}_name_size,
			          error );
#endif
			if( result != 1 )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
				 "%s: unable to retrieve ${mount_tool_file_entry_type_description} name size.",
				 function );

				goto on_error;
			}
			${mount_tool_file_entry_type}_name = system_string_allocate(
			                                      ${mount_tool_file_entry_type}_name_size );

			if( ${mount_tool_file_entry_type}_name == NULL )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_MEMORY,
				 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
				 "%s: unable to create ${mount_tool_file_entry_type_description} name string.",
				 function );

				goto on_error;
			}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
			result = libolecf_${mount_tool_file_entry_type}_get_utf16_name(
			          ${mount_tool_file_entry_type},
			          (uint16_t *) ${mount_tool_file_entry_type}_name,
			          ${mount_tool_file_entry_type}_name_size,
			          error );
#else
			result = libolecf_${mount_tool_file_entry_type}_get_utf8_name(
			          ${mount_tool_file_entry_type},
			          (uint8_t *) ${mount_tool_file_entry_type}_name,
			          ${mount_tool_file_entry_type}_name_size,
			          error );
#endif
			if( result != 1 )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
				 "%s: unable to retrieve ${mount_tool_file_entry_type_description} name.",
				 function );

				goto on_error;
			}
			if( mount_file_system_get_sanitized_filename(
			     mount_handle->file_system,
			     ${mount_tool_file_entry_type}_name,
			     ${mount_tool_file_entry_type}_name_size - 1,
			     &filename,
			     &filename_size,
			     error ) != 1 )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
				 "%s: unable to retrieve filename.",
				 function );

				goto on_error;
			}
			memory_free(
			 ${mount_tool_file_entry_type}_name );

			${mount_tool_file_entry_type}_name = NULL;
		}
