
#if defined( __cplusplus )
extern "C" {
#endif

#if defined( __APPLE__ ) && defined( FUSE_DARWIN_ENABLE_EXTENSIONS ) && FUSE_DARWIN_ENABLE_EXTENSIONS == 1
typedef struct fuse_darwin_attr mount_fuse_stat_t;
#elif defined( __CYGWIN__ ) && defined( FUSE_MAJOR_VERSION ) && FUSE_MAJOR_VERSION >= 3
typedef struct fuse_stat mount_fuse_stat_t;
#else
typedef struct stat mount_fuse_stat_t;
#endif

#if defined( __APPLE__ ) && defined( FUSE_DARWIN_ENABLE_EXTENSIONS ) && FUSE_DARWIN_ENABLE_EXTENSIONS == 1
#define mount_fuse_fill_dir_t fuse_darwin_fill_dir_t
#else
#define mount_fuse_fill_dir_t fuse_fill_dir_t
#endif

#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBFUSE3 ) || defined( HAVE_LIBOSXFUSE )

