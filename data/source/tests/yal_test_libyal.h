/*
 * The internal ${library_name} header
 *
 * Copyright (C) ${copyright}, ${tests_authors}
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

#if !defined( _${library_name_suffix_upper_case}_TEST_${library_name_upper_case}_H )
#define _${library_name_suffix_upper_case}_TEST_${library_name_upper_case}_H

#include <common.h>

/* If Cygwin libtool DLL support is enabled and do not want to create static
 * executables set ${library_name_upper_case}_DLL_IMPORT before including ${library_name}.h
 */
#if defined( _WIN32 ) && defined( DLL_EXPORT ) && !defined( HAVE_STATIC_EXECUTABLES )
#define ${library_name_upper_case}_DLL_IMPORT
#endif

#include <${library_name}.h>

#endif /* !defined( _${library_name_suffix_upper_case}_TEST_${library_name_upper_case}_H ) */

