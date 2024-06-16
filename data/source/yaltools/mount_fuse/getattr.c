/* Retrieves the file stat info
 * Returns 0 if successful or a negative errno value otherwise
 */
#if defined( HAVE_LIBFUSE3 )
int mount_fuse_getattr(
     const char *path,
     struct stat *stat_info,
     struct fuse_file_info *file_info ${tools_name:upper_case}_ATTRIBUTE_UNUSED )
#else
int mount_fuse_getattr(
     const char *path,
     struct stat *stat_info )
#endif
{
	libcerror_error_t *error       = NULL;
	mount_file_entry_t *file_entry = NULL;
	static char *function          = "mount_fuse_getattr";
	size64_t file_size             = 0;
	uint64_t access_time           = 0;
	uint64_t inode_change_time     = 0;
	uint64_t modification_time     = 0;
	uint16_t file_mode             = 0;
	int result                     = 0;

#if defined( HAVE_LIBFUSE3 )
	${tools_name:upper_case}_UNREFERENCED_PARAMETER( file_info )
#endif

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
	if( stat_info == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid stat info.",
		 function );

		result = -EINVAL;

		goto on_error;
	}
	if( memory_set(
	     stat_info,
	     0,
	     sizeof( struct stat ) ) == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to clear stat info.",
		 function );

		result = errno;

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
	if( mount_file_entry_get_size(
	     file_entry,
	     &file_size,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve file entry size.",
		 function );

		result = -EIO;

		goto on_error;
	}
	if( mount_file_entry_get_file_mode(
	     file_entry,
	     &file_mode,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve file mode.",
		 function );

		result = -EIO;

		goto on_error;
	}
	if( mount_file_entry_get_access_time(
	     file_entry,
	     &access_time,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve access time.",
		 function );

		result = -EIO;

		goto on_error;
	}
	if( mount_file_entry_get_modification_time(
	     file_entry,
	     &modification_time,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve modification time.",
		 function );

		result = -EIO;

		goto on_error;
	}
	if( mount_file_entry_get_inode_change_time(
	     file_entry,
	     &inode_change_time,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve inode change time.",
		 function );

		result = -EIO;

		goto on_error;
	}
	if( mount_fuse_set_stat_info(
	     stat_info,
	     file_size,
	     file_mode,
	     (int64_t) access_time,
	     (int64_t) inode_change_time,
	     (int64_t) modification_time,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set stat info.",
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

