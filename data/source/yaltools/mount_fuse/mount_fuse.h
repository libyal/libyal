/*
 * Mount tool fuse functions
 *
 * Copyright (C) ${copyright}, ${tools_authors}
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#if !defined( _MOUNT_FUSE_H )
#define _MOUNT_FUSE_H

#include <common.h>
#include <types.h>

#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBOSXFUSE )

/* Ensure FUSE_USE_VERSION is defined before including fuse.h
 */
#if !defined( FUSE_USE_VERSION )
#warning FUSE_USE_VERSION not set, defaulting to 26
#define FUSE_USE_VERSION	26
#endif

#if defined( HAVE_LIBFUSE )
#include <fuse.h>
#elif defined( HAVE_LIBOSXFUSE )
#include <osxfuse/fuse.h>
#endif

#endif /* defined( HAVE_LIBFUSE ) || defined( HAVE_LIBOSXFUSE ) */

#include "mount_file_entry.h"
#include "mount_handle.h"
#include "${tools_name}_libcerror.h"
#include "${tools_name}_${library_name}.h"

#if defined( __cplusplus )
extern "C" {
#endif

#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBOSXFUSE )

int mount_fuse_set_stat_info(
     struct stat *stat_info,
     size64_t size,
     uint16_t file_mode,
     int64_t access_time,
     int64_t inode_change_time,
     int64_t modification_time,
     libcerror_error_t **error );

int mount_fuse_filldir(
     void *buffer,
     fuse_fill_dir_t filler,
     const char *name,
     struct stat *stat_info,
     mount_file_entry_t *file_entry,
     libcerror_error_t **error );

int mount_fuse_open(
     const char *path,
     struct fuse_file_info *file_info );

int mount_fuse_read(
     const char *path,
     char *buffer,
     size_t size,
     off_t offset,
     struct fuse_file_info *file_info );

int mount_fuse_release(
     const char *path,
     struct fuse_file_info *file_info );

int mount_fuse_opendir(
     const char *path,
     struct fuse_file_info *file_info );

#if FUSE_USE_VERSION >= 30
int mount_fuse_readdir(
     const char *path,
     void *buffer,
     fuse_fill_dir_t filler,
     off_t offset,
     struct fuse_file_info *file_info,
     enum fuse_readdir_flags flags );
#else
int mount_fuse_readdir(
     const char *path,
     void *buffer,
     fuse_fill_dir_t filler,
     off_t offset,
     struct fuse_file_info *file_info );
#endif

int mount_fuse_releasedir(
     const char *path,
     struct fuse_file_info *file_info );

#if FUSE_USE_VERSION >= 30
int mount_fuse_getattr(
     const char *path,
     struct stat *stat_info,
     struct fuse_file_info *file_info );
#else
int mount_fuse_getattr(
     const char *path,
     struct stat *stat_info );
#endif

void mount_fuse_destroy(
      void *private_data );

#endif /* defined( HAVE_LIBFUSE ) || defined( HAVE_LIBOSXFUSE ) */

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _MOUNT_FUSE_H ) */

