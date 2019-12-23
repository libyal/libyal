#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

static int (*cthreads_test_real_pthread_cond_init)(pthread_cond_t *, const pthread_condattr_t *) = NULL;
static int (*cthreads_test_real_pthread_cond_destroy)(pthread_cond_t *)                          = NULL;
static int (*cthreads_test_real_pthread_cond_broadcast)(pthread_cond_t *)                        = NULL;
static int (*cthreads_test_real_pthread_cond_signal)(pthread_cond_t *)                           = NULL;
static int (*cthreads_test_real_pthread_cond_wait)(pthread_cond_t *, pthread_mutex_t *)          = NULL;

int cthreads_test_pthread_cond_init_attempts_before_fail                                         = -1;
int cthreads_test_pthread_cond_destroy_attempts_before_fail                                      = -1;
int cthreads_test_pthread_cond_broadcast_attempts_before_fail                                    = -1;
int cthreads_test_pthread_cond_signal_attempts_before_fail                                       = -1;
int cthreads_test_pthread_cond_wait_attempts_before_fail                                         = -1;

int cthreads_test_real_pthread_cond_init_function_return_value                                   = EBUSY;
int cthreads_test_real_pthread_cond_destroy_function_return_value                                = EBUSY;

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

/* Custom pthread_cond_init for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_cond_init(
     pthread_cond_t *cond,
     const pthread_condattr_t *attr )
{
	int result = 0;

	if( cthreads_test_real_pthread_cond_init == NULL )
	{
		cthreads_test_real_pthread_cond_init = dlsym(
		                                        RTLD_NEXT,
		                                        "pthread_cond_init" );
	}
	if( cthreads_test_pthread_cond_init_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_cond_init_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_cond_init_function_return_value );
	}
	else if( cthreads_test_pthread_cond_init_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_cond_init_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_cond_init(
	          cond,
	          attr );

	return( result );
}

/* Custom pthread_cond_destroy for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_cond_destroy(
     pthread_cond_t *cond )
{
	int result = 0;

	if( cthreads_test_real_pthread_cond_destroy == NULL )
	{
		cthreads_test_real_pthread_cond_destroy = dlsym(
		                                           RTLD_NEXT,
		                                           "pthread_cond_destroy" );
	}
	if( cthreads_test_pthread_cond_destroy_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_cond_destroy_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_cond_destroy_function_return_value );
	}
	else if( cthreads_test_pthread_cond_destroy_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_cond_destroy_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_cond_destroy(
	          cond );

	return( result );
}

/* Custom pthread_cond_broadcast for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_cond_broadcast(
     pthread_cond_t *cond )
{
	int result = 0;

	if( cthreads_test_real_pthread_cond_broadcast == NULL )
	{
		cthreads_test_real_pthread_cond_broadcast = dlsym(
		                                             RTLD_NEXT,
		                                             "pthread_cond_broadcast" );
	}
	if( cthreads_test_pthread_cond_broadcast_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_cond_broadcast_attempts_before_fail = -1;

		return( EBUSY );
	}
	else if( cthreads_test_pthread_cond_broadcast_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_cond_broadcast_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_cond_broadcast(
	          cond );

	return( result );
}

/* Custom pthread_cond_signal for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_cond_signal(
     pthread_cond_t *cond )
{
	int result = 0;

	if( cthreads_test_real_pthread_cond_signal == NULL )
	{
		cthreads_test_real_pthread_cond_signal = dlsym(
		                                          RTLD_NEXT,
		                                          "pthread_cond_signal" );
	}
	if( cthreads_test_pthread_cond_signal_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_cond_signal_attempts_before_fail = -1;

		return( EBUSY );
	}
	else if( cthreads_test_pthread_cond_signal_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_cond_signal_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_cond_signal(
	          cond );

	return( result );
}

/* Custom pthread_cond_wait for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_cond_wait(
     pthread_cond_t *cond,
     pthread_mutex_t *mutex )
{
	int result = 0;

	if( cthreads_test_real_pthread_cond_wait == NULL )
	{
		cthreads_test_real_pthread_cond_wait = dlsym(
		                                        RTLD_NEXT,
		                                        "pthread_cond_wait" );
	}
	if( cthreads_test_pthread_cond_wait_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_cond_wait_attempts_before_fail = -1;

		return( EBUSY );
	}
	else if( cthreads_test_pthread_cond_wait_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_cond_wait_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_cond_wait(
	          cond,
	          mutex );

	return( result );
}

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

