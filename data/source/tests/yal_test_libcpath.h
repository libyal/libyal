/*
 * The internal libcpath header
 *
 * Copyright (C) ${copyright}, ${authors}
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This software is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this software.  If not, see <http://www.gnu.org/licenses/>.
 */

#if !defined( _${library_name_suffix_upper_case}_TEST_LIBCPATH_H )
#define _${library_name_suffix_upper_case}_TEST_LIBCPATH_H

#include <common.h>

/* Define HAVE_LOCAL_LIBCPATH for local use of libcpath
 */
#if defined( HAVE_LOCAL_LIBCPATH )

#include <libcpath_definitions.h>
#include <libcpath_path.h>

#else

/* If libtool DLL support is enabled set LIBCPATH_DLL_IMPORT
 * before including libcpath.h
 */
#if defined( _WIN32 ) && defined( DLL_IMPORT )
#define LIBCPATH_DLL_IMPORT
#endif

#include <libcpath.h>

#endif /* !defined( _${library_name_suffix_upper_case}_TEST_LIBCPATH_H ) */

#endif /* !defined( _${library_name_suffix_upper_case}_TEST_LIBCPATH_H ) */

