#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

static int (*cthreads_test_real_pthread_mutex_init)(pthread_mutex_t *, const pthread_mutexattr_t *) = NULL;
static int (*cthreads_test_real_pthread_mutex_destroy)(pthread_mutex_t *)                           = NULL;
static int (*cthreads_test_real_pthread_mutex_lock)(pthread_mutex_t *)                              = NULL;
static int (*cthreads_test_real_pthread_mutex_unlock)(pthread_mutex_t *)                            = NULL;

int cthreads_test_pthread_mutex_init_attempts_before_fail                                           = -1;
int cthreads_test_pthread_mutex_destroy_attempts_before_fail                                        = -1;
int cthreads_test_pthread_mutex_lock_attempts_before_fail                                           = -1;
int cthreads_test_pthread_mutex_unlock_attempts_before_fail                                         = -1;

int cthreads_test_real_pthread_mutex_init_function_return_value                                     = EBUSY;
int cthreads_test_real_pthread_mutex_destroy_function_return_value                                  = EBUSY;
int cthreads_test_real_pthread_mutex_lock_function_return_value                                     = EBUSY;
int cthreads_test_real_pthread_mutex_unlock_function_return_value                                   = EBUSY;

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

libcthreads_lock_t *cthreads_test_lock = NULL;
int cthreads_test_locked_value         = 0;

#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

/* Custom pthread_mutex_init for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_mutex_init(
     pthread_mutex_t *mutex,
     const pthread_mutexattr_t *attr )
{
	int result = 0;

	if( cthreads_test_real_pthread_mutex_init == NULL )
	{
		cthreads_test_real_pthread_mutex_init = dlsym(
		                                         RTLD_NEXT,
		                                         "pthread_mutex_init" );
	}
	if( cthreads_test_pthread_mutex_init_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_mutex_init_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_mutex_init_function_return_value );
	}
	else if( cthreads_test_pthread_mutex_init_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_mutex_init_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_mutex_init(
	          mutex,
	          attr );

	return( result );
}

/* Custom pthread_mutex_destroy for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_mutex_destroy(
     pthread_mutex_t *mutex )
{
	int result = 0;

	if( cthreads_test_real_pthread_mutex_destroy == NULL )
	{
		cthreads_test_real_pthread_mutex_destroy = dlsym(
		                                            RTLD_NEXT,
		                                            "pthread_mutex_destroy" );
	}
	if( cthreads_test_pthread_mutex_destroy_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_mutex_destroy_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_mutex_destroy_function_return_value );
	}
	else if( cthreads_test_pthread_mutex_destroy_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_mutex_destroy_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_mutex_destroy(
	          mutex );

	return( result );
}

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

		return( cthreads_test_real_pthread_mutex_lock_function_return_value );
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

		return( cthreads_test_real_pthread_mutex_unlock_function_return_value );
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

/* The thread1 callback function
 * Returns 1 if successful or -1 on error
 */
int cthreads_test_lock_callback_function1(
     void *arguments CTHREADS_TEST_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "cthreads_test_lock_callback_function1";
	int result               = 0;

	CTHREADS_TEST_UNREFERENCED_PARAMETER( arguments )

	result = libcthreads_lock_grab(
	          cthreads_test_lock,
	          &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to grab lock.",
		 function );

		goto on_error;
	}
	cthreads_test_locked_value += 19;

	result = libcthreads_lock_release(
		  cthreads_test_lock,
		  &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to release lock.",
		 function );

		goto on_error;
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

/* The thread2 callback function
 * Returns 1 if successful or -1 on error
 */
int cthreads_test_lock_callback_function2(
     void *arguments CTHREADS_TEST_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "cthreads_test_lock_callback_function2";
	int result               = 0;

	CTHREADS_TEST_UNREFERENCED_PARAMETER( arguments )

	result = libcthreads_lock_grab(
	          cthreads_test_lock,
	          &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to grab lock.",
		 function );

		goto on_error;
	}
	cthreads_test_locked_value += 38;

	result = libcthreads_lock_release(
		  cthreads_test_lock,
		  &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to release lock.",
		 function );

		goto on_error;
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

