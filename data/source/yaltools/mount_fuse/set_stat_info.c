#if ( SIZEOF_OFF_T != 8 ) && ( SIZEOF_OFF_T != 4 )
#error Size of off_t not supported
#endif

/* Sets the values in a stat info structure
 * The time values are a signed 64-bit POSIX date and time value in number of nanoseconds
 * Returns 1 if successful or -1 on error
 */
int mount_fuse_set_stat_info(
     struct stat *stat_info,
     size64_t size,
     uint16_t file_mode,
     int64_t access_time,
     int64_t inode_change_time,
     int64_t modification_time,
     libcerror_error_t **error )
{
	static char *function = "mount_fuse_set_stat_info";

	if( stat_info == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid stat info.",
		 function );

		return( -1 );
	}
#if SIZEOF_OFF_T <= 4
	if( size > (size64_t) UINT32_MAX )
#else
	if( size > (size64_t) INT64_MAX )
#endif
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid size value out of bounds.",
		 function );

		return( -1 );
	}
	stat_info->st_size  = (off_t) size;
	stat_info->st_mode  = file_mode;

	if( ( file_mode & 0x4000 ) != 0 )
	{
		stat_info->st_nlink = 2;
	}
	else
	{
		stat_info->st_nlink = 1;
	}
#if defined( HAVE_GETEUID )
	stat_info->st_uid = geteuid();
#endif
#if defined( HAVE_GETEGID )
	stat_info->st_gid = getegid();
#endif

	stat_info->st_atime = access_time / 1000000000;
	stat_info->st_ctime = inode_change_time / 1000000000;
	stat_info->st_mtime = modification_time / 1000000000;

#if defined( STAT_HAVE_NSEC )
	stat_info->st_atime_nsec = access_time % 1000000000;
	stat_info->st_ctime_nsec = inode_change_time % 1000000000;
	stat_info->st_mtime_nsec = modification_time % 1000000000;
#endif
	return( 1 );
}

