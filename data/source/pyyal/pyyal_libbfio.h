/*
 * The libbfio header wrapper
 *
 * Copyright (C) ${python_module_copyright}, ${python_module_authors}
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

#if !defined( _${python_module_name:upper_case}_LIBBFIO_H )
#define _${python_module_name:upper_case}_LIBBFIO_H

#include <common.h>

/* Define HAVE_LOCAL_LIBBFIO for local use of libbfio
 */
#if defined( HAVE_LOCAL_LIBBFIO )

#include <libbfio_definitions.h>
#include <libbfio_file.h>
#include <libbfio_file_pool.h>
#include <libbfio_file_range.h>
#include <libbfio_handle.h>
#include <libbfio_memory_range.h>
#include <libbfio_pool.h>
#include <libbfio_types.h>

#else

/* If libtool DLL support is enabled set LIBBFIO_DLL_IMPORT
 * before including libbfio.h
 */
#if defined( _WIN32 ) && defined( DLL_IMPORT )
#define LIBBFIO_DLL_IMPORT
#endif

#include <libbfio.h>

#endif /* defined( HAVE_LOCAL_LIBBFIO ) */

#endif /* !defined( _${python_module_name:upper_case}_LIBBFIO_H ) */

