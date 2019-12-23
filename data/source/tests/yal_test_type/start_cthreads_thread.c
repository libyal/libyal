#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

static int (*cthreads_test_real_pthread_thread_create)(pthread_t *, const pthread_attr_t *, void *(*)(void *), void *) = NULL;
static int (*cthreads_test_real_pthread_thread_join)(pthread_t, void **)                                               = NULL;

int cthreads_test_pthread_thread_create_attempts_before_fail                                                           = -1;
int cthreads_test_pthread_thread_join_attempts_before_fail                                                             = -1;

int cthreads_test_real_pthread_thread_create_function_return_value                                                     = EBUSY;
int cthreads_test_real_pthread_thread_join_function_return_value                                                       = EBUSY;

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

/* Custom pthread_thread_create for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_thread_create(
     pthread_t *thread,
     const pthread_attr_t *attr,
     void *(*start_routine)(void *),
     void **arg )
{
	int result = 0;

	if( cthreads_test_real_pthread_thread_create == NULL )
	{
		cthreads_test_real_pthread_thread_create = dlsym(
		                                            RTLD_NEXT,
		                                            "pthread_thread_create" );
	}
	if( cthreads_test_pthread_thread_create_attempts_before_fail == 0 )
	{
		cthreads_test_pthread_thread_create_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_thread_create_function_return_value );
	}
	else if( cthreads_test_pthread_thread_create_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_thread_create_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_thread_create(
	          thread,
	          attr,
	          start_routine,
	          arg );

	return( result );
}

/* Custom pthread_thread_join for testing error cases
 * Returns 0 if successful or an error value otherwise
 */
int pthread_thread_join(
     pthread_t thread,
     void **retval )
{
	int result = 0;

	if( cthreads_test_real_pthread_thread_join == NULL )
	{
		cthreads_test_real_pthread_thread_join = dlsym(
		                                          RTLD_NEXT,
		                                          "pthread_thread_join" );
	}
	if( cthreads_test_pthread_thread_join_attempts_before_fail == 0 )
	{
		/* Join the thread otherwise it can enter a nondeterministic state
		 */
		cthreads_test_real_pthread_thread_join(
		 thread,
		 retval );

		cthreads_test_pthread_thread_join_attempts_before_fail = -1;

		return( cthreads_test_real_pthread_thread_join_function_return_value );
	}
	else if( cthreads_test_pthread_thread_join_attempts_before_fail > 0 )
	{
		cthreads_test_pthread_thread_join_attempts_before_fail--;
	}
	result = cthreads_test_real_pthread_thread_join(
	          thread,
	          retval );

	return( result );
}

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

/* The thread callback function
 * Returns 1 if successful or -1 on error
 */
int cthreads_test_thread_callback_function(
     void *arguments CTHREADS_TEST_ATTRIBUTE_UNUSED )
{
	CTHREADS_TEST_UNREFERENCED_PARAMETER( arguments )

	return( 1 );
}

