#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

static int (*cthreads_test_real_pthread_mutex_lock)(pthread_mutex_t *)   = NULL;
static int (*cthreads_test_real_pthread_mutex_unlock)(pthread_mutex_t *) = NULL;

int cthreads_test_pthread_mutex_lock_attempts_before_fail                = -1;
int cthreads_test_pthread_mutex_unlock_attempts_before_fail              = -1;

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

libcthreads_queue_t *cthreads_test_queue = NULL;
int cthreads_test_expected_queued_value  = 0;
int cthreads_test_queued_value           = 0;
int cthreads_test_number_of_iterations   = 497;
int cthreads_test_number_of_values       = 32;

#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

/* Custom pthread_mutex_lock for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_mutex_lock(
     pthread_mutex_t *mutex )
{
	int result = 0;

	if( cthreads_test_real_pthread_mutex_lock == NULL )
	{
		cthreads_test_real_pthread_mutex_lock = dlsym(
		                                         RTLD_NEXT,
		                                         "pthread_mutex_lock" );
	}
	if( cthreads_test_pthread_mutex_lock_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_mutex_lock_attempts_before_fail = -1;

		return( EBUSY );
	}
	else if( cthreads_test_pthread_mutex_lock_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_mutex_lock_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_mutex_lock(
	          mutex );

	return( result );
}

/* Custom pthread_mutex_unlock for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_mutex_unlock(
     pthread_mutex_t *mutex )
{
	int result = 0;

	if( cthreads_test_real_pthread_mutex_unlock == NULL )
	{
		cthreads_test_real_pthread_mutex_unlock = dlsym(
		                                           RTLD_NEXT,
		                                           "pthread_mutex_unlock" );
	}
	if( cthreads_test_pthread_mutex_unlock_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_mutex_unlock_attempts_before_fail = -1;

		return( EBUSY );
	}
	else if( cthreads_test_pthread_mutex_unlock_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_mutex_unlock_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_mutex_unlock(
	          mutex );

	return( result );
}

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

/* Test element compare function
 * Returns LIBCTHREADS_COMPARE_LESS, LIBCTHREADS_COMPARE_EQUAL, LIBCTHREADS_COMPARE_GREATER if successful or -1 on error
 */
int cthreads_test_queue_value_compare_function(
     int *first_value,
     int *second_value,
     libcthreads_error_t **error )
{
	static char *function = "cthreads_test_queue_value_compare_function";

	if( first_value == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid first value.",
		 function );

		return( -1 );
	}
	if( second_value == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid second value.",
		 function );

		return( -1 );
	}
	if( *first_value > *second_value )
	{
		return( LIBCTHREADS_COMPARE_LESS );
	}
	else if( *first_value < *second_value )
	{
		return( LIBCTHREADS_COMPARE_GREATER );
	}
	return( LIBCTHREADS_COMPARE_EQUAL );
}

/* The thread pop callback function
 * Returns 1 if successful or -1 on error
 */
int cthreads_test_queue_pop_callback_function(
     void *arguments CTHREADS_TEST_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "cthreads_test_queue_pop_callback_function";
	int *queued_value        = NULL;
	int iterator             = 0;

	CTHREADS_TEST_UNREFERENCED_PARAMETER( arguments )

	for( iterator = 0;
	     iterator < cthreads_test_number_of_iterations;
	     iterator++ )
	{
		if( libcthreads_queue_pop(
		     cthreads_test_queue,
		     (intptr_t **) &queued_value,
		     &error ) == -1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_REMOVE_FAILED,
			 "%s: unable to pop value off queue.",
			 function );

			goto on_error;
		}
		cthreads_test_queued_value += *queued_value;
	}
	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_backtrace_fprint(
		 error,
		 stdout );

		libcerror_error_free(
		 &error );
	}
	return( -1 );
}

/* The thread push callback function
 * Returns 1 if successful or -1 on error
 */
int cthreads_test_queue_push_callback_function(
     int *queued_values )
{
	libcerror_error_t *error = NULL;
	static char *function    = "cthreads_test_queue_push_callback_function";
	int iterator             = 0;

	for( iterator = 0;
	     iterator < cthreads_test_number_of_iterations;
	     iterator++ )
	{
		queued_values[ iterator ] = ( 98 * iterator ) % 45;

		if( libcthreads_queue_push(
		     cthreads_test_queue,
		     (intptr_t *) &( queued_values[ iterator ] ),
		     &error ) == -1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_APPEND_FAILED,
			 "%s: unable to get value from queue.",
			 function );

			goto on_error;
		}
		cthreads_test_expected_queued_value += queued_values[ iterator ];
	}
	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_backtrace_fprint(
		 error,
		 stdout );

		libcerror_error_free(
		 &error );
	}
	return( -1 );
}

