/*
 * The internal type definitions
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

#if !defined( _${library_name_upper_case}_INTERNAL_TYPES_H )
#define _${library_name_upper_case}_INTERNAL_TYPES_H

#include <common.h>
#include <types.h>

/* Define HAVE_LOCAL_${library_name_upper_case} for local use of ${library_name}
 * The definitions in <${library_name}/types.h> are copied here
 * for local use of ${library_name}
 */
#if defined( HAVE_LOCAL_${library_name_upper_case} )

/* The following type definitions hide internal data structures
 */
#if defined( HAVE_DEBUG_OUTPUT ) && !defined( WINAPI )
typedef struct ${library_name}_type {}		${library_name}_type_t;

#else
typedef intptr_t ${library_name}_type_t;

#endif /* defined( HAVE_DEBUG_OUTPUT ) && !defined( WINAPI ) */

#endif /* defined( HAVE_LOCAL_${library_name_upper_case} ) */

#endif /* !defined( _${library_name_upper_case}_INTERNAL_TYPES_H ) */

