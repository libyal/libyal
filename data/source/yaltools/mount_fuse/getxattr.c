/* Retrieves the value data of an extended attribute
 * Returns 0 if successful or a negative errno value otherwise
 */
int mount_fuse_getxattr(
     const char *path,
     const char *name,
     char *value,
     size_t size )
{
	libcerror_error_t *error                                 = NULL;
	${library_name}_extended_attribute_t *extended_attribute = NULL;
	mount_file_entry_t *file_entry                           = NULL;
	static char *function                                    = "mount_fuse_getxattr";
	size64_t value_data_size                                 = 0;
	size_t name_length                                       = 0;
	ssize_t read_count                                       = 0;
	int result                                               = 0;

#if defined( HAVE_DEBUG_OUTPUT )
	if( libcnotify_verbose != 0 )
	{
		libcnotify_printf(
		 "%s: %s (%s)\n",
		 function,
		 path,
		 name );
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
	if( name == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid name.",
		 function );

		result = -EINVAL;

		goto on_error;
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
	name_length = narrow_string_length(
	               name );

	result = ${library_name}_file_entry_get_extended_attribute_by_utf8_name(
	          file_entry->${mount_tool_file_entry_type_name},
	          (uint8_t *) name,
	          name_length,
	          &extended_attribute,
	          &error );

	if( result == -1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve extended attribute.",
		 function );

		result = -EIO;

		goto on_error;
	}
	else if( result != 0 )
	{
		if( ${library_name}_extended_attribute_get_size(
		     extended_attribute,
		     &value_data_size,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve extended attribute value data size.",
			 function );

			result = -EIO;

			goto on_error;
		}
		if( value_data_size > (size64_t) INT_MAX )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
			 "%s: invalid value data size value out of bounds.",
			 function );

			result = -E2BIG;

			goto on_error;
		}
		/* When size is 0 determine and return the required value size
		 */
		if( size == 0 )
		{
			read_count = (ssize_t) value_data_size;
		}
		else
		{
			if( (size64_t) size < value_data_size )
			{
				libcerror_error_set(
				 &error,
				 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
				 LIBCERROR_ARGUMENT_ERROR_VALUE_TOO_SMALL,
				 "%s: invalid size value too small.",
				 function );

				result = -ERANGE;

				goto on_error;
			}
			read_count = ${library_name}_extended_attribute_read_buffer_at_offset(
			              extended_attribute,
			              (void *) value,
			              size,
			              0,
			              &error );

			if( read_count == -1 )
			{
				libcerror_error_set(
				 &error,
				 LIBCERROR_ERROR_DOMAIN_IO,
				 LIBCERROR_IO_ERROR_READ_FAILED,
				 "%s: unable to read from extended attribute.",
				 function );

				result = -EIO;

				goto on_error;
			}
		}
	}
	if( ${library_name}_extended_attribute_free(
	     &extended_attribute,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
		 "%s: unable to free extended attribute.",
		 function );

		result = -EIO;

		goto on_error;
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
	if( result == 0 )
	{
		return( -ENODATA );
	}
	return( (int) read_count );

on_error:
	if( error != NULL )
	{
		libcnotify_print_error_backtrace(
		 error );
		libcerror_error_free(
		 &error );
	}
	if( file_entry != NULL )
	{
		mount_file_entry_free(
		 &file_entry,
		 NULL );
	}
	return( result );
}

