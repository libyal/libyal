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

#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBFUSE3 ) || defined( HAVE_LIBOSXFUSE )

#if !defined( FUSE_USE_VERSION ) && !defined( CYGFUSE )

/* Ensure FUSE_USE_VERSION is defined before including fuse.h
 */
#if defined( HAVE_LIBFUSE3 )
#define FUSE_USE_VERSION	30
#else
#define FUSE_USE_VERSION	26
#endif

#endif /* !defined( FUSE_USE_VERSION ) && !defined( CYGFUSE ) */

#if defined( HAVE_LIBFUSE ) || defined( HAVE_LIBFUSE3 )
#include <fuse.h>
#elif defined( HAVE_LIBOSXFUSE )
#include <osxfuse/fuse.h>
#endif

#endif /* defined( HAVE_LIBFUSE ) || defined( HAVE_LIBFUSE3 ) || defined( HAVE_LIBOSXFUSE ) */

