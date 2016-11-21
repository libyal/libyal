/*
 * The internal extern definition
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

#if !defined( _${library_name_upper_case}_INTERNAL_EXTERN_H )
#define _${library_name_upper_case}_INTERNAL_EXTERN_H

#include <common.h>

/* Define HAVE_LOCAL_${library_name_upper_case} for local use of ${library_name}
 */
#if !defined( HAVE_LOCAL_${library_name_upper_case} )

/* If libtool DLL support is enabled set ${library_name_upper_case}_DLL_EXPORT
 * before including ${library_name}/extern.h
 */
#if defined( _WIN32 ) && defined( DLL_EXPORT )
#define ${library_name_upper_case}_DLL_EXPORT
#endif

#include <${library_name}/extern.h>

#else
#define ${library_name_upper_case}_EXTERN	/* extern */

#endif /* !defined( HAVE_LOCAL_${library_name_upper_case} ) */

#endif /* !defined( _${library_name_upper_case}_INTERNAL_EXTERN_H ) */

