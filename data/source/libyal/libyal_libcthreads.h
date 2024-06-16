/*
 * The libcthreads header wrapper
 *
 * Copyright (C) ${copyright}, ${authors}
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

#if !defined( _${library_name:upper_case}_LIBCTHREADS_H )
#define _${library_name:upper_case}_LIBCTHREADS_H

#include <common.h>

#if defined( HAVE_MULTI_THREAD_SUPPORT ) && !defined( HAVE_LOCAL_${library_name:upper_case} )
#define HAVE_${library_name:upper_case}_MULTI_THREAD_SUPPORT
#endif

#if defined( HAVE_${library_name:upper_case}_MULTI_THREAD_SUPPORT )

/* Define HAVE_LOCAL_LIBCTHREADS for local use of libcthreads
 */
#if defined( HAVE_LOCAL_LIBCTHREADS )

#include <libcthreads_condition.h>
#include <libcthreads_definitions.h>
#include <libcthreads_lock.h>
#include <libcthreads_mutex.h>
#include <libcthreads_read_write_lock.h>
#include <libcthreads_queue.h>
#include <libcthreads_thread.h>
#include <libcthreads_thread_attributes.h>
#include <libcthreads_thread_pool.h>
#include <libcthreads_types.h>

#else

/* If libtool DLL support is enabled set LIBCTHREADS_DLL_IMPORT
 * before including libcthreads.h
 */
#if defined( _WIN32 ) && defined( DLL_IMPORT )
#define LIBCTHREADS_DLL_IMPORT
#endif

#include <libcthreads.h>

#endif /* defined( HAVE_LOCAL_LIBCTHREADS ) */

#endif /* defined( HAVE_${library_name:upper_case}_MULTI_THREAD_SUPPORT ) */

#endif /* !defined( _${library_name:upper_case}_LIBCTHREADS_H ) */

