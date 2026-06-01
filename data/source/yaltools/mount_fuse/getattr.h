#if defined( HAVE_LIBFUSE3 )
int mount_fuse_getattr(
     const char *path,
     mount_fuse_stat_t *stat_info,
     struct fuse_file_info *file_info );
#else
int mount_fuse_getattr(
     const char *path,
     mount_fuse_stat_t *stat_info );
#endif

