#if ( SIZEOF_OFF_T != 8 ) && ( SIZEOF_OFF_T != 4 )
#error Size of off_t not supported
#endif

/* Sets the values in a stat info structure
 * The time values are a signed 64-bit POSIX date and time value in number of nanoseconds
 * Returns 1 if successful or -1 on error
 */
int mount_fuse_set_stat_info(
     mount_fuse_stat_t *stat_info,
     size64_t size,
     uint16_t file_mode,
     int64_t access_time,
     int64_t inode_change_time,
     int64_t modification_time,
     libcerror_error_t **error )
{
	static char *function = "mount_fuse_set_stat_info";
	int group_identifier  = 0;
	int number_of_links   = 0;
	int owner_identifier  = 0;

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
	if( ( file_mode & 0x4000 ) != 0 )
	{
		number_of_links = 2;
	}
	else
	{
		number_of_links = 1;
	}
#if defined( HAVE_GETEUID )
	owner_identifier = geteuid();
#endif
#if defined( HAVE_GETEGID )
	group_identifier = getegid();
#endif
#if defined( __APPLE__ )
	stat_info->size  = (off_t) size;
	stat_info->mode  = file_mode;
	stat_info->nlink = number_of_links;
	stat_info->uid   = owner_identifier;
	stat_info->gid   = group_identifier;

	stat_info->atimespec.tv_sec  = access_time / 1000000000;
	stat_info->atimespec.tv_nsec = access_time % 1000000000;

	stat_info->ctimespec.tv_sec  = inode_change_time / 1000000000;
	stat_info->ctimespec.tv_nsec = inode_change_time % 1000000000;

	stat_info->mtimespec.tv_sec  = modification_time / 1000000000;
	stat_info->mtimespec.tv_nsec = modification_time % 1000000000;
#else
	stat_info->st_size  = (off_t) size;
	stat_info->st_mode  = file_mode;
	stat_info->st_nlink = number_of_links;
	stat_info->st_uid   = owner_identifier;
	stat_info->st_gid   = group_identifier;

	stat_info->st_atime = access_time / 1000000000;
	stat_info->st_ctime = inode_change_time / 1000000000;
	stat_info->st_mtime = modification_time / 1000000000;

#if defined( STAT_HAVE_NSEC )
	stat_info->st_atime_nsec = access_time % 1000000000;
	stat_info->st_ctime_nsec = inode_change_time % 1000000000;
	stat_info->st_mtime_nsec = modification_time % 1000000000;
#endif
#endif /* defined( __APPLE__ ) */

	return( 1 );
}

