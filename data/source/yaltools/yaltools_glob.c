/*
 * Globbing functions
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

#include <common.h>
#include <memory.h>
#include <narrow_string.h>
#include <system_string.h>
#include <types.h>
#include <wide_string.h>

#if defined( HAVE_ERRNO_H ) || defined( WINAPI )
#include <errno.h>
#endif

#if defined( HAVE_STDLIB_H ) || defined( WINAPI )
#include <stdlib.h>
#endif

#if defined( HAVE_IO_H ) || defined( WINAPI )
#include <io.h>
#endif

#include "${tools_name}_find.h"
#include "${tools_name}_glob.h"
#include "${tools_name}_libcerror.h"

/* TODO rename */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
#if defined( _MSC_VER )
#define ${tools_name}_path_make( path, path_size, drive, directory, filename, extension ) \
	_wmakepath_s( path, path_size, drive, directory, filename, extension )

#define ${tools_name}_path_split( path, drive, drive_size, directory, directory_size, filename, filename_size, extension, extension_size ) \
	_wsplitpath_s( path, drive, drive_size, directory, directory_size, filename, filename_size, extension, extension_size )

#else
#define ${tools_name}_path_make( path, path_size, drive, directory, filename, extension ) \
	_wmakepath( path, drive, directory, filename, extension )

#define ${tools_name}_path_split( path, drive, drive_size, directory, directory_size, filename, filename_size, extension, extension_size ) \
	_wsplitpath( path, drive, directory, filename, extension )

#endif

#else
#if defined( _MSC_VER )
#define ${tools_name}_path_make( path, path_size, drive, directory, filename, extension ) \
	_makepath_s( path, path_size, drive, directory, filename, extension )

#define ${tools_name}_path_split( path, drive, drive_size, directory, directory_size, filename, filename_size, extension, extension_size ) \
	_splitpath_s( path, drive, drive_size, directory, directory_size, filename, filename_size, extension, extension_size )

#else
#define ${tools_name}_path_make( path, path_size, drive, directory, filename, extension ) \
	_makepath( path, drive, directory, filename, extension )

#define ${tools_name}_path_split( path, drive, drive_size, directory, directory_size, filename, filename_size, extension, extension_size ) \
	_splitpath( path, drive, directory, filename, extension )

#endif
#endif

#if !defined( HAVE_GLOB_H )

/* Creates a glob
 * Make sure the value glob is referencing, is set to NULL
 * Returns 1 if successful or -1 on error
 */
int ${tools_name}_glob_initialize(
     ${tools_name}_glob_t **glob,
     libcerror_error_t **error )
{
	static char *function = "${tools_name}_glob_initialize";

	if( glob == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid glob.",
		 function );

		return( -1 );
	}
	if( *glob != NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_ALREADY_SET,
		 "%s: invalid glob value already set.",
		 function );

		return( -1 );
	}
	*glob = memory_allocate_structure(
	         ${tools_name}_glob_t );

	if( *glob == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create glob.",
		 function );

		goto on_error;
	}
	if( memory_set(
	     *glob,
	     0,
	     sizeof( ${tools_name}_glob_t ) ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to clear glob.",
		 function );

		goto on_error;
	}
	return( 1 );

on_error:
	if( *glob != NULL )
	{
		memory_free(
		 *glob );

		*glob = NULL;
	}
	return( -1 );
}

/* Frees a glob
 * Returns 1 if successful or -1 on error
 */
int ${tools_name}_glob_free(
     ${tools_name}_glob_t **glob,
     libcerror_error_t **error )
{
	static char *function = "${tools_name}_glob_free";
	int result_iterator   = 0;

	if( glob == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid glob.",
		 function );

		return( -1 );
	}
	if( *glob != NULL )
	{
		if( ( *glob )->results != NULL )
		{
			for( result_iterator = 0;
			     result_iterator < ( *glob )->number_of_results;
			     result_iterator++ )
			{
				if( ( *glob )->results[ result_iterator ] != NULL )
				{
					memory_free(
					 ( *glob )->results[ result_iterator ] );
				}
			}
			memory_free(
			 ( *glob )->results );
		}
		memory_free(
		 *glob );

		*glob = NULL;
	}
	return( 1 );
}

/* Resizes the glob
 * Returns 1 if successful or -1 on error
 */
int ${tools_name}_glob_resize(
     ${tools_name}_glob_t *glob,
     int new_number_of_results,
     libcerror_error_t **error )
{
	void *reallocation    = NULL;
	static char *function = "${tools_name}_glob_resize";
	size_t previous_size  = 0;
	size_t new_size       = 0;

	if( glob == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid glob.",
		 function );

		return( -1 );
	}
	if( glob->number_of_results >= new_number_of_results )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: new number of results less equal than current.",
		 function );

		return( -1 );
	}
	previous_size = sizeof( system_character_t * ) * glob->number_of_results;
	new_size      = sizeof( system_character_t * ) * new_number_of_results;

	if( ( previous_size > (size_t) SSIZE_MAX )
	 || ( new_size > (size_t) SSIZE_MAX ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid size value exceeds maximum.",
		 function );

		return( -1 );
	}
	reallocation = memory_reallocate(
	                glob->results,
	                new_size );

	if( reallocation == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to reallocate glob results.",
		 function );

		return( -1 );
	}
	glob->results = (system_character_t **) reallocation;

	if( memory_set(
	     &( glob->results[ glob->number_of_results ] ),
	     0,
	     new_size - previous_size ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to clear glob.",
		 function );

		return( -1 );
	}
	glob->number_of_results = new_number_of_results;

	return( 1 );
}

/* Resolves filenames with wildcards (globs)
 * Returns 1 if successful or -1 on error
 */
int ${tools_name}_glob_resolve(
     ${tools_name}_glob_t *glob,
     system_character_t * const patterns[],
     int number_of_patterns,
     libcerror_error_t **error )
{
#if defined( HAVE_IO_H ) || defined( WINAPI )
	${tools_name}_find_data_t find_data;

	system_character_t find_path[ _MAX_PATH ];
	system_character_t find_drive[ _MAX_DRIVE ];
	system_character_t find_directory[ _MAX_DIR ];
	system_character_t find_name[ _MAX_FNAME ];
	system_character_t find_extension[ _MAX_EXT ];

	intptr_t find_handle    = 0;
#endif
	static char *function   = "${tools_name}_glob_resolve";
	size_t find_path_length = 0;
	int globs_found         = 0;
	int iterator            = 0;

	if( glob == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid glob.",
		 function );

		return( -1 );
	}
	for( iterator = 0;
	     iterator < number_of_patterns;
	     iterator++ )
	{
		if( patterns[ iterator ] == NULL )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
			 "%s: missing pattern value.",
			 function );

			return( -1 );
		}
#if defined( _MSC_VER )
		if( ${tools_name}_path_split(
		     patterns[ iterator ],
		     find_drive,
		     _MAX_DRIVE,
		     find_directory,
		     _MAX_DIR,
		     find_name,
		     _MAX_FNAME,
		     find_extension,
		     _MAX_EXT ) != 0 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to split path.",
			 function );

			return( -1 );
		}
#else
		${tools_name}_path_split(
		 patterns[ iterator ],
		 find_drive,
		 _MAX_DRIVE,
		 find_directory,
		 _MAX_DIR,
		 find_name,
		 _MAX_FNAME,
		 find_extension,
		 _MAX_EXT );
#endif
		find_handle = ${tools_name}_find_first(
		               patterns[ iterator ],
		               &find_data );

		if( find_handle != -1 )
		{
			do
			{
				if( ${tools_name}_glob_resize(
				     glob,
				     glob->number_of_results + 1,
				     error ) != 1 )
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_RESIZE_FAILED,
					 "%s: unable to resize glob.",
					 function );

					return( -1 );
				}
#if defined( _MSC_VER )
				if( ${tools_name}_path_make(
				     find_path,
				     _MAX_PATH,
				     find_drive,
				     find_directory,
				     find_data.name,
				     _SYSTEM_STRING( "" )  ) != 0 )
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
					 "%s: unable to make path.",
					 function );

					return( -1 );
				}
#elif defined( __BORLANDC__ ) && __BORLANDC__ <= 0x0520
				${tools_name}_path_make(
				 find_path,
				 _MAX_PATH,
				 find_drive,
				 find_directory,
				 find_data.ff_name,
				 _SYSTEM_STRING( "" ) );

#else
				${tools_name}_path_make(
				 find_path,
				 _MAX_PATH,
				 find_drive,
				 find_directory,
				 find_data.name,
				 _SYSTEM_STRING( "" ) );
#endif

				find_path_length = system_string_length(
				                    find_path );

				glob->results[ glob->number_of_results - 1 ] = system_string_allocate(
				                                                                  find_path_length + 1 );

				if( glob->results[ glob->number_of_results - 1 ] == NULL )
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_MEMORY,
					 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
					 "%s: unable to create glob result.",
					 function );

					return( -1 );
				}
				if( system_string_copy(
				     glob->results[ glob->number_of_results - 1 ],
				     find_path,
				     find_path_length ) == NULL )
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
					 "%s: unable to set glob result.",
					 function );

					memory_free(
					 glob->results[ glob->number_of_results - 1 ] );

					glob->results[ glob->number_of_results - 1 ] = NULL;

					return( -1 );
				}
				( glob->results[ glob->number_of_results - 1 ] )[ find_path_length ] = 0;

				globs_found++;

				if( globs_found > (int32_t) UINT16_MAX )
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: too many globs found.",
					 function );

					return( -1 );
				}
			}
			while( ${tools_name}_find_next(
			        find_handle,
			        &find_data ) == 0 );

			if( errno != ENOENT )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
				 "%s: error finding next file entry.",
				 function );

				return( -1 );
			}
			if( ${tools_name}_find_close(
			     find_handle ) != 0 )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
				 "%s: error closing find handle.",
				 function );

				return( -1 );
			}
		}
		else if( errno != ENOENT )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: error finding file entry.",
			 function );

			return( -1 );
		}
	}
	return( 1 );
}

/* Retrieves the glob results
 * Returns 1 if successful or -1 on error
 */
int ${tools_name}_glob_get_results(
     ${tools_name}_glob_t *glob,
     int *number_of_results,
     system_character_t ***results,
     libcerror_error_t **error )
{
	static char *function = "${tools_name}_glob_resize";

	if( glob == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid glob.",
		 function );

		return( -1 );
	}
	if( number_of_results == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid number of results.",
		 function );

		return( -1 );
	}
	if( results == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid results.",
		 function );

		return( -1 );
	}
	*number_of_results = glob->number_of_results;
	*results           = glob->results;

	return( 1 );
}

#endif /* !defined( HAVE_GLOB_H ) */

