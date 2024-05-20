#if defined( HAVE_LIBFUSE3 )
int mount_fuse_getattr(
     const char *path,
     struct stat *stat_info,
     struct fuse_file_info *file_info );
#else
int mount_fuse_getattr(
     const char *path,
     struct stat *stat_info );
#endif

