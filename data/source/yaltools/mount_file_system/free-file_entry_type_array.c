		if( libcdata_array_free(
		     &( ( *file_system )->${mount_tool_file_entry_type}s_array ),
		     NULL,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
			 "%s: unable to free ${mount_tool_file_entry_type_description}s array.",
			 function );

			result = -1;
		}
