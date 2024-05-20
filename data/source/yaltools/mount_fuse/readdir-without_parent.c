/* Reads a directory
 * Returns 0 if successful or a negative errno value otherwise
 */
#if defined( HAVE_LIBFUSE3 )
int mount_fuse_readdir(
     const char *path,
     void *buffer,
     fuse_fill_dir_t filler,
     off_t offset ${tools_name_upper_case}_ATTRIBUTE_UNUSED,
     struct fuse_file_info *file_info ${tools_name_upper_case}_ATTRIBUTE_UNUSED,
     enum fuse_readdir_flags flags ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
#else
int mount_fuse_readdir(
     const char *path,
     void *buffer,
     fuse_fill_dir_t filler,
     off_t offset ${tools_name_upper_case}_ATTRIBUTE_UNUSED,
     struct fuse_file_info *file_info ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
#endif
{
	struct stat *stat_info             = NULL;
	libcerror_error_t *error           = NULL;
	mount_file_entry_t *sub_file_entry = NULL;
	static char *function              = "mount_fuse_readdir";
	char *name                         = NULL;
	size_t name_size                   = 0;
	int number_of_sub_file_entries     = 0;
	int result                         = 0;
	int sub_file_entry_index           = 0;

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( offset )

#if defined( HAVE_LIBFUSE3 )
	${tools_name_upper_case}_UNREFERENCED_PARAMETER( flags )
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
	if( file_info == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file information.",
		 function );

		result = -EINVAL;

		goto on_error;
	}
	if( file_info->fh == (uint64_t) NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
		 "%s: invalid file information - missing file handle.",
		 function );

		result = -EINVAL;

		goto on_error;
	}
	stat_info = memory_allocate_structure(
	             struct stat );

	if( stat_info == NULL )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create stat info.",
		 function );

		result = errno;

		goto on_error;
	}
	if( mount_fuse_filldir(
	     buffer,
	     filler,
	     ".",
	     stat_info,
	     (mount_file_entry_t *) file_info->fh,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set self directory entry.",
		 function );

		result = -EIO;

		goto on_error;
	}
	if( mount_fuse_filldir(
	     buffer,
	     filler,
	     "..",
	     stat_info,
	     NULL,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set parent directory entry.",
		 function );

		result = -EIO;

		goto on_error;
	}
	if( mount_file_entry_get_number_of_sub_file_entries(
	     (mount_file_entry_t *) file_info->fh,
	     &number_of_sub_file_entries,
	     &error ) != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of sub file entries.",
		 function );

		result = -EIO;

		goto on_error;
	}
	for( sub_file_entry_index = 0;
	     sub_file_entry_index < number_of_sub_file_entries;
	     sub_file_entry_index++ )
	{
		if( mount_file_entry_get_sub_file_entry_by_index(
		     (mount_file_entry_t *) file_info->fh,
		     sub_file_entry_index,
		     &sub_file_entry,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve sub file entry: %d.",
			 function,
			 sub_file_entry_index );

			result = -EIO;

			goto on_error;
		}
		if( mount_file_entry_get_name_size(
		     sub_file_entry,
		     &name_size,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve sub file entry: %d name size.",
			 function,
			 sub_file_entry_index );

			result = -EIO;

			goto on_error;
		}
		name = narrow_string_allocate(
		        name_size );

		if( name == NULL )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_MEMORY,
			 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
			 "%s: unable to create sub file entry: %d name.",
			 function );

			result = -EIO;

			goto on_error;
		}
		if( mount_file_entry_get_name(
		     sub_file_entry,
		     name,
		     name_size,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve sub file entry: %d name.",
			 function,
			 sub_file_entry_index );

			result = -EIO;

			goto on_error;
		}
		if( mount_fuse_filldir(
		     buffer,
		     filler,
		     name,
		     stat_info,
		     sub_file_entry,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to set directory entry.",
			 function );

			result = -EIO;

			goto on_error;
		}
		memory_free(
		 name );

		name = NULL;

		if( mount_file_entry_free(
		     &sub_file_entry,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
			 "%s: unable to free sub file entry: %d.",
			 function,
			 sub_file_entry_index );

			result = -EIO;

			goto on_error;
		}
	}
	memory_free(
	 stat_info );

	return( 0 );

on_error:
	if( error != NULL )
	{
		libcnotify_print_error_backtrace(
		 error );
		libcerror_error_free(
		 &error );
	}
	if( name != NULL )
	{
		memory_free(
		 name );
	}
	if( sub_file_entry != NULL )
	{
		mount_file_entry_free(
		 &sub_file_entry,
		 NULL );
	}
	if( stat_info != NULL )
	{
		memory_free(
		 stat_info );
	}
	return( result );
}

