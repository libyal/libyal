
#if defined( __cplusplus )
extern "C" {
#endif

#if defined( _WIN32 ) || defined( WINFSP_VERSION )
typedef struct fuse_stat mount_fuse_stat_t;
#else
typedef struct stat mount_fuse_stat_t;
#endif

#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBFUSE3 ) || defined( HAVE_LIBOSXFUSE )

