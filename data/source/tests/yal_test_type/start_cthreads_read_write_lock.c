#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

static int (*cthreads_test_real_pthread_rwlock_init)(pthread_rwlock_t *, const pthread_rwlockattr_t *) = NULL;
static int (*cthreads_test_real_pthread_rwlock_destroy)(pthread_rwlock_t *)                            = NULL;
static int (*cthreads_test_real_pthread_rwlock_rdlock)(pthread_rwlock_t *)                             = NULL;
static int (*cthreads_test_real_pthread_rwlock_wrlock)(pthread_rwlock_t *)                             = NULL;
static int (*cthreads_test_real_pthread_rwlock_unlock)(pthread_rwlock_t *)                             = NULL;

int cthreads_test_pthread_rwlock_init_attempts_before_fail                                             = -1;
int cthreads_test_pthread_rwlock_destroy_attempts_before_fail                                          = -1;
int cthreads_test_pthread_rwlock_rdlock_attempts_before_fail                                           = -1;
int cthreads_test_pthread_rwlock_wrlock_attempts_before_fail                                           = -1;
int cthreads_test_pthread_rwlock_unlock_attempts_before_fail                                           = -1;

int cthreads_test_real_pthread_rwlock_init_function_return_value                                       = EBUSY;
int cthreads_test_real_pthread_rwlock_destroy_function_return_value                                    = EBUSY;
int cthreads_test_real_pthread_rwlock_rdlock_function_return_value                                     = EBUSY;
int cthreads_test_real_pthread_rwlock_wrlock_function_return_value                                     = EBUSY;
int cthreads_test_real_pthread_rwlock_unlock_function_return_value                                     = EBUSY;

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

libcthreads_read_write_lock_t *cthreads_test_read_write_lock = NULL;
int cthreads_test_locked_value                               = 0;

#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

/* Custom pthread_rwlock_init for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_rwlock_init(
     pthread_rwlock_t *rwlock,
     const pthread_rwlockattr_t *attr )
{
	int result = 0;

	if( cthreads_test_real_pthread_rwlock_init == NULL )
	{
		cthreads_test_real_pthread_rwlock_init = dlsym(
		                                          RTLD_NEXT,
		                                          "pthread_rwlock_init" );
	}
	if( cthreads_test_pthread_rwlock_init_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_rwlock_init_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_rwlock_init_function_return_value );
	}
	else if( cthreads_test_pthread_rwlock_init_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_rwlock_init_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_rwlock_init(
	          rwlock,
	          attr );

	return( result );
}

/* Custom pthread_rwlock_destroy for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_rwlock_destroy(
     pthread_rwlock_t *rwlock )
{
	int result = 0;

	if( cthreads_test_real_pthread_rwlock_destroy == NULL )
	{
		cthreads_test_real_pthread_rwlock_destroy = dlsym(
		                                             RTLD_NEXT,
		                                             "pthread_rwlock_destroy" );
	}
	if( cthreads_test_pthread_rwlock_destroy_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_rwlock_destroy_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_rwlock_destroy_function_return_value );
	}
	else if( cthreads_test_pthread_rwlock_destroy_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_rwlock_destroy_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_rwlock_destroy(
	          rwlock );

	return( result );
}

/* Custom pthread_rwlock_rdlock for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_rwlock_rdlock(
     pthread_rwlock_t *rwlock )
{
	int result = 0;

	if( cthreads_test_real_pthread_rwlock_rdlock == NULL )
	{
		cthreads_test_real_pthread_rwlock_rdlock = dlsym(
		                                            RTLD_NEXT,
		                                            "pthread_rwlock_rdlock" );
	}
	if( cthreads_test_pthread_rwlock_rdlock_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_rwlock_rdlock_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_rwlock_rdlock_function_return_value );
	}
	else if( cthreads_test_pthread_rwlock_rdlock_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_rwlock_rdlock_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_rwlock_rdlock(
	          rwlock );

	return( result );
}

/* Custom pthread_rwlock_wrlock for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_rwlock_wrlock(
     pthread_rwlock_t *rwlock )
{
	int result = 0;

	if( cthreads_test_real_pthread_rwlock_wrlock == NULL )
	{
		cthreads_test_real_pthread_rwlock_wrlock = dlsym(
		                                            RTLD_NEXT,
		                                            "pthread_rwlock_wrlock" );
	}
	if( cthreads_test_pthread_rwlock_wrlock_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_rwlock_wrlock_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_rwlock_wrlock_function_return_value );
	}
	else if( cthreads_test_pthread_rwlock_wrlock_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_rwlock_wrlock_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_rwlock_wrlock(
	          rwlock );

	return( result );
}

/* Custom pthread_rwlock_unlock for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_rwlock_unlock(
     pthread_rwlock_t *rwlock )
{
	int result = 0;

	if( cthreads_test_real_pthread_rwlock_unlock == NULL )
	{
		cthreads_test_real_pthread_rwlock_unlock = dlsym(
		                                            RTLD_NEXT,
		                                            "pthread_rwlock_unlock" );
	}
	if( cthreads_test_pthread_rwlock_unlock_attempts_before_fail == 0 )
	{
		/* Unlock the read/write lock otherwise it can enter a nondeterministic state
		 */
		cthreads_test_real_pthread_rwlock_unlock(
		 rwlock );

		cthreads_test_pthread_rwlock_unlock_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_rwlock_unlock_function_return_value );
	}
	else if( cthreads_test_pthread_rwlock_unlock_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_rwlock_unlock_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_rwlock_unlock(
	          rwlock );

	return( result );
}

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

/* The cthreads_test_read_write_lock_grab_for_read thread1 callback function
 * Returns 1 if successful or -1 on error
 */
int cthreads_test_read_write_lock_grab_for_read_callback_function1(
     void *arguments CTHREADS_TEST_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "cthreads_test_read_write_lock_grab_for_read_callback_function1";
	int result               = 0;

	CTHREADS_TEST_UNREFERENCED_PARAMETER( arguments )

	result = libcthreads_read_write_lock_grab_for_read(
	          cthreads_test_read_write_lock,
	          &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to grab read/write lock.",
		 function );

		goto on_error;
	}
	result = libcthreads_read_write_lock_release_for_read(
		  cthreads_test_read_write_lock,
		  &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to release read/write lock.",
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

/* The cthreads_test_read_write_lock_grab_for_read thread2 callback function
 * Returns 1 if successful or -1 on error
 */
int cthreads_test_read_write_lock_grab_for_read_callback_function2(
     void *arguments CTHREADS_TEST_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "cthreads_test_read_write_lock_grab_for_read_callback_function2";
	int result               = 0;

	CTHREADS_TEST_UNREFERENCED_PARAMETER( arguments )

	result = libcthreads_read_write_lock_grab_for_read(
	          cthreads_test_read_write_lock,
	          &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to grab read/write lock.",
		 function );

		goto on_error;
	}
	result = libcthreads_read_write_lock_release_for_read(
		  cthreads_test_read_write_lock,
		  &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to release read/write lock.",
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

/* The cthreads_test_read_write_lock_grab_for_write thread1 callback function
 * Returns 1 if successful or -1 on error
 */
int cthreads_test_read_write_lock_grab_for_write_callback_function1(
     void *arguments CTHREADS_TEST_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "cthreads_test_read_write_lock_grab_for_write_callback_function1";
	int result               = 0;

	CTHREADS_TEST_UNREFERENCED_PARAMETER( arguments )

	result = libcthreads_read_write_lock_grab_for_write(
	          cthreads_test_read_write_lock,
	          &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to grab read/write lock.",
		 function );

		goto on_error;
	}
	cthreads_test_locked_value += 19;

	result = libcthreads_read_write_lock_release_for_write(
		  cthreads_test_read_write_lock,
		  &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to release read/write lock.",
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

/* The cthreads_test_read_write_lock_grab_for_write thread2 callback function
 * Returns 1 if successful or -1 on error
 */
int cthreads_test_read_write_lock_grab_for_write_callback_function2(
     void *arguments CTHREADS_TEST_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "cthreads_test_read_write_lock_grab_for_write_callback_function2";
	int result               = 0;

	CTHREADS_TEST_UNREFERENCED_PARAMETER( arguments )

	result = libcthreads_read_write_lock_grab_for_write(
	          cthreads_test_read_write_lock,
	          &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to grab read/write lock.",
		 function );

		goto on_error;
	}
	cthreads_test_locked_value += 38;

	result = libcthreads_read_write_lock_release_for_write(
		  cthreads_test_read_write_lock,
		  &error );

	if( result != 1 )
	{
		libcerror_error_set(
		 &error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to release read/write lock.",
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

