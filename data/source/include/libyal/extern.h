/*
 * The extern definition
 *
 * This header should be included in header files that export or import
 * library functions
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

#if !defined( _${library_name:upper_case}_EXTERN_H )
#define _${library_name:upper_case}_EXTERN_H

/* To export functions from the ${library_name} DLL define ${library_name:upper_case}_DLL_EXPORT
 * To import functions from the ${library_name} DLL define ${library_name:upper_case}_DLL_IMPORT
 * Otherwise use default extern statement
 */
#if defined( ${library_name:upper_case}_DLL_EXPORT )
#define ${library_name:upper_case}_EXTERN __declspec(dllexport)

#elif defined( ${library_name:upper_case}_DLL_IMPORT )
#define ${library_name:upper_case}_EXTERN extern __declspec(dllimport)

#else
#define ${library_name:upper_case}_EXTERN extern

#endif

#endif /* !defined( _${library_name:upper_case}_EXTERN_H ) */

