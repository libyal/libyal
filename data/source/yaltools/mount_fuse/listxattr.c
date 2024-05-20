/* Lists the names of extended attributes
 * Returns 0 if successful or a negative errno value otherwise
 */
int mount_fuse_listxattr(
     const char *path,
     char *list,
     size_t size )
{
	libcerror_error_t *error                                 = NULL;
	${library_name}_extended_attribute_t *extended_attribute = NULL;
	mount_file_entry_t *file_entry                           = NULL;
	static char *function                                    = "mount_fuse_listxattr";
	size_t extended_attribute_name_size                      = 0;
	size_t list_offset                                       = 0;
	int extended_attribute_index                             = 0;
	int number_of_extended_attributes                        = 0;
	int result                                               = 0;

#if defined( HAVE_DEBUG_OUTPUT )
	if( libcnotify_verbose != 0 )
	{
		libcnotify_printf(
		 "%s: %s\n",
		 function,
		 path );
	}
#endif
	if( path == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid path.",
		 function );

		result = -EINVAL;

		goto on_error;
	}
	/* When size is 0 determine and return the required list size
	 */
	if( size > 0 )
	{
		if( list == NULL )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
			 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
			 "%s: invalid list.",
			 function );

			result = -EINVAL;

			goto on_error;
		}
	}
	if( size > (size_t) INT_MAX )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid size value exceeds maximum.",
		 function );

		result = -EINVAL;

		goto on_error;
	}
	result = mount_handle_get_file_entry_by_path(
	          ${mount_tool_name}_mount_handle,
	          path,
	          &file_entry,
	          &error );

	if( result == -1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve value for: %s.",
		 function,
		 path );

		result = -ENOENT;

		goto on_error;
	}
	else if( result == 0 )
	{
		return( -ENOENT );
	}
	if( ${library_name}_file_entry_get_number_of_extended_attributes(
	     file_entry->${mount_tool_file_entry_type_name},
	     &number_of_extended_attributes,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of extended attributes.",
		 function );

		result = -EIO;

		goto on_error;
	}
	for( extended_attribute_index = 0;
	     extended_attribute_index < number_of_extended_attributes;
	     extended_attribute_index++ )
	{
		if( ${library_name}_file_entry_get_extended_attribute_by_index(
		     file_entry->${mount_tool_file_entry_type_name},
		     extended_attribute_index,
		     &extended_attribute,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve extended attribute: %d.",
			 function,
			 extended_attribute_index );

			result = -EIO;

			goto on_error;
		}
		if( ${library_name}_extended_attribute_get_utf8_name_size(
		     extended_attribute,
		     &extended_attribute_name_size,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve extended attribute: %d name string size.",
			 function,
			 extended_attribute_index );

			result = -EIO;

			goto on_error;
		}
		if( size > 0 )
		{
			if( extended_attribute_name_size > ( size - list_offset ) )
			{
				libcerror_error_set(
				 &error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid extended attribute name size value out of bounds.",
				 function );

				result = -EIO;

				goto on_error;
			}
			if( ${library_name}_extended_attribute_get_utf8_name(
			     extended_attribute,
			     (uint8_t *) &( list[ list_offset ] ),
			     extended_attribute_name_size,
			     &error ) != 1 )
			{
				libcerror_error_set(
				 &error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
				 "%s: unable to retrieve extended attribute name: %d string.",
				 function,
				 extended_attribute_index );

				result = -EIO;

				goto on_error;
			}
		}
		list_offset += extended_attribute_name_size;

		if( ${library_name}_extended_attribute_free(
		     &extended_attribute,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
			 "%s: unable to free extended attribute: %d.",
			 function,
			 extended_attribute_index );

			result = -EIO;

			goto on_error;
		}
	}
	if( mount_file_entry_free(
	     &file_entry,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
		 "%s: unable to free file entry.",
		 function );

		result = -EIO;

		goto on_error;
	}
	return( (int) list_offset );

on_error:
	if( error != NULL )
	{
		libcnotify_print_error_backtrace(
		 error );
		libcerror_error_free(
		 &error );
	}
	if( extended_attribute != NULL )
	{
		${library_name}_extended_attribute_free(
		 &extended_attribute,
		 NULL );
	}
	if( file_entry != NULL )
	{
		mount_file_entry_free(
		 &file_entry,
		 NULL );
	}
	return( result );
}

