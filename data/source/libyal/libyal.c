/*
 * ${library_description}
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

#include <common.h>

#if defined( WINAPI )
#include <windows.h>
#endif

#include "${library_name}_unused.h"

/* Define HAVE_LOCAL_${library_name:upper_case} for local use of ${library_name}
 */
#if !defined( HAVE_LOCAL_${library_name:upper_case} )

#if defined( WINAPI ) && defined( HAVE_DLLMAIN )

#if defined( _MANAGED )
#pragma managed( push, off )
#endif

/* Defines the entry point for the DLL
 */
BOOL WINAPI DllMain(
             HINSTANCE hinstDLL,
             DWORD fdwReason,
             LPVOID lpvReserved )
{
	${library_name:upper_case}_UNREFERENCED_PARAMETER( lpvReserved )

	switch( fdwReason )
	{
		case DLL_PROCESS_ATTACH:
			DisableThreadLibraryCalls(
			 hinstDLL );
			break;

		case DLL_THREAD_ATTACH:
			break;

		case DLL_THREAD_DETACH:
			break;

		case DLL_PROCESS_DETACH:
			break;
	}
	return( TRUE );
}

/* Function that indicates the library is a DLL
 * Returns 1
 */
int ${library_name}_is_dll(
     void )
{
	return( 1 );
}

#endif /* defined( WINAPI ) && defined( HAVE_DLLMAIN ) */

#endif /* !defined( HAVE_LOCAL_${library_name:upper_case} ) */

