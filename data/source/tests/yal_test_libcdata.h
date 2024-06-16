/*
 * The libcdata header wrapper
 *
 * Copyright (C) ${copyright}, ${tests_authors}
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

#if !defined( _${library_name_suffix:upper_case}_TEST_LIBCDATA_H )
#define _${library_name_suffix:upper_case}_TEST_LIBCDATA_H

#include <common.h>

/* Define HAVE_LOCAL_LIBCDATA for local use of libcdata
 */
#if defined( HAVE_LOCAL_LIBCDATA )

#include <libcdata_array.h>
#include <libcdata_btree.h>
#include <libcdata_definitions.h>
#include <libcdata_list.h>
#include <libcdata_list_element.h>
#include <libcdata_range_list.h>
#include <libcdata_tree_node.h>
#include <libcdata_types.h>

#else

/* If libtool DLL support is enabled set LIBCDATA_DLL_IMPORT
 * before including libcdata.h
 */
#if defined( _WIN32 ) && defined( DLL_IMPORT )
#define LIBCDATA_DLL_IMPORT
#endif

#include <libcdata.h>

#endif /* defined( HAVE_LOCAL_LIBCDATA ) */

#endif /* !defined( _${library_name_suffix:upper_case}_TEST_LIBCDATA_H ) */

