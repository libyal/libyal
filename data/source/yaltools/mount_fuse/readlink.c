/* Reads the target of a symbolic link
 * Returns 0 if successful or a negative errno value otherwise
 */
int mount_fuse_readlink(
     const char *path,
     char *buffer,
     size_t size )
{
	libcerror_error_t *error       = NULL;
	mount_file_entry_t *file_entry = NULL;
	static char *function          = "mount_fuse_readlink";
	int result                     = 0;

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
	if( mount_file_entry_get_symbolic_link_target(
	     file_entry,
	     buffer,
	     size,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve symbolic link target string.",
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
	return( 0 );

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

