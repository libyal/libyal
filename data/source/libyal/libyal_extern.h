/*
 * The internal extern definition
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

#if !defined( _${library_name:upper_case}_INTERNAL_EXTERN_H )
#define _${library_name:upper_case}_INTERNAL_EXTERN_H

#include <common.h>

#if !defined( __CYGWIN__ ) && !defined( _WIN32 ) && defined( __has_attribute )
#if __has_attribute( visibility )
#define ${library_name:upper_case}_INTERNAL	__attribute__((visibility("hidden"))) extern

#else
#define ${library_name:upper_case}_INTERNAL	extern

#endif /* __has_attribute( visibility ) */
#else
#define ${library_name:upper_case}_INTERNAL	extern

#endif /* !defined( __CYGWIN__ ) && !defined( _WIN32 ) && defined( __has_attribute ) */

/* Define HAVE_LOCAL_${library_name:upper_case} for local use of ${library_name}
 */
#if !defined( HAVE_LOCAL_${library_name:upper_case} )

#include <${library_name}/extern.h>

#else
#define ${library_name:upper_case}_EXTERN		/* extern */
#define ${library_name:upper_case}_EXTERN_VARIABLE	${library_name:upper_case}_INTERNAL

#endif /* !defined( HAVE_LOCAL_${library_name:upper_case} ) */

#endif /* !defined( _${library_name:upper_case}_INTERNAL_EXTERN_H ) */

