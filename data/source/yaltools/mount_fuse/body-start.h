
#if defined( __cplusplus )
extern "C" {
#endif

#if defined( _WIN32 ) || defined( WINFSP_VERSION )
typedef struct fuse_stat mount_fuse_stat_t;
#elif defined( __APPLE__ )
typedef struct fuse_darwin_attr mount_fuse_stat_t;
#else
typedef struct stat mount_fuse_stat_t;
#endif

#if defined( __APPLE__ )
#define mount_fuse_fill_dir_t fuse_darwin_fill_dir_t
#else
#define mount_fuse_fill_dir_t fuse_fill_dir_t
#endif

#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBFUSE3 ) || defined( HAVE_LIBOSXFUSE )

