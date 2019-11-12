/*
 * Signal handling functions
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

#if !defined( _${tools_name_upper_case}_SIGNAL_H )
#define _${tools_name_upper_case}_SIGNAL_H

#include <common.h>
#include <types.h>

#include "${tools_name}_libcerror.h"

#if defined( __cplusplus )
extern "C" {
#endif

#if !defined( HAVE_SIGNAL_H ) && !defined( WINAPI )
#error missing signal functions
#endif

#if defined( WINAPI )
typedef unsigned long ${tools_name}_signal_t;

#else
typedef int ${tools_name}_signal_t;

#endif /* defined( WINAPI ) */

#if defined( WINAPI )

BOOL WINAPI ${tools_name}_signal_handler(
             ${tools_name}_signal_t signal );

#if defined( _MSC_VER )

void ${tools_name}_signal_initialize_memory_debug(
      void );

#endif /* defined( _MSC_VER ) */

#endif /* defined( WINAPI ) */

int ${tools_name}_signal_attach(
     void (*signal_handler)( ${tools_name}_signal_t ),
     libcerror_error_t **error );

int ${tools_name}_signal_detach(
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${tools_name_upper_case}_SIGNAL_H ) */

