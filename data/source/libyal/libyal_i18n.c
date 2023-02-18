/*
 * Internationalization (i18n) functions
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
#include <types.h>

#if defined( HAVE_LIBINTL_H ) && defined( ENABLE_NLS )
#include <libintl.h>
#endif

#include "${library_name}_i18n.h"
#include "${library_name}_libcerror.h"

static int ${library_name}_i18n_initialized = 0;

/* Initializes library internationalization functions
 */
int ${library_name}_i18n_initialize(
     libcerror_error_t **error )
{
	static char *function = "${library_name}_i18n_initialize";

	if( ${library_name}_i18n_initialized == 0 )
	{
#if defined( HAVE_BINDTEXTDOMAIN ) && defined( LOCALEDIR )
		if( bindtextdomain(
		     "${library_name}",
		     LOCALEDIR ) == NULL )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to bind text domain.",
			 function );

			return( -1 );
		}
#endif /* defined( HAVE_BINDTEXTDOMAIN ) && defined( LOCALEDIR ) */

		${library_name}_i18n_initialized = 1;
	}
	return( 1 );
}

