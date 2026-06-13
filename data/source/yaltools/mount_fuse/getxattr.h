#if defined( __APPLE__ )
int mount_fuse_getxattr(
     const char *path,
     const char *name,
     char *value,
     size_t size,
     uint32_t position );
#else
int mount_fuse_getxattr(
     const char *path,
     const char *name,
     char *value,
     size_t size );
#endif

