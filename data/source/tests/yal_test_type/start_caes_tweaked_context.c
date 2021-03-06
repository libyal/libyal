#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

#if defined( HAVE_LIBCRYPTO ) && defined( HAVE_OPENSSL_EVP_H ) && defined( HAVE_EVP_CRYPTO_AES_XTS )

static int (*caes_test_real_EVP_CIPHER_CTX_set_padding)(EVP_CIPHER_CTX *, int)                                                                    = NULL;
static int (*caes_test_real_EVP_CipherInit_ex)(EVP_CIPHER_CTX *, const EVP_CIPHER *, ENGINE *, const unsigned char *, const unsigned char *, int) = NULL;
static int (*caes_test_real_EVP_CipherUpdate)(EVP_CIPHER_CTX *, unsigned char *, int *, const unsigned char *, int)                               = NULL;

int caes_test_EVP_CIPHER_CTX_set_padding_attempts_before_fail                                                                                     = -1;
int caes_test_EVP_CipherInit_ex_attempts_before_fail                                                                                              = -1;
int caes_test_EVP_CipherUpdate_attempts_before_fail                                                                                               = -1;

#endif /* defined( HAVE_LIBCRYPTO ) && defined( HAVE_OPENSSL_EVP_H ) && defined( HAVE_EVP_CRYPTO_AES_XTS ) */

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ )

#if defined( HAVE_LIBCRYPTO ) && defined( HAVE_OPENSSL_EVP_H ) && defined( HAVE_EVP_CRYPTO_AES_XTS )

/* Custom EVP_CIPHER_CTX_set_padding for testing error cases
 * Returns 1 if successful or 0 otherwise
 */
int EVP_CIPHER_CTX_set_padding(
     EVP_CIPHER_CTX *c,
     int pad )
{
	int result = 0;

	if( caes_test_real_EVP_CIPHER_CTX_set_padding == NULL )
	{
		caes_test_real_EVP_CIPHER_CTX_set_padding = dlsym(
		                                             RTLD_NEXT,
		                                             "EVP_CIPHER_CTX_set_padding" );
	}
	if( caes_test_EVP_CIPHER_CTX_set_padding_attempts_before_fail == 0 )
	{
		caes_test_EVP_CIPHER_CTX_set_padding_attempts_before_fail = -1;

		return( 0 );
	}
	else if( caes_test_EVP_CIPHER_CTX_set_padding_attempts_before_fail > 0 )
	{
		caes_test_EVP_CIPHER_CTX_set_padding_attempts_before_fail--;
	}
	result = caes_test_real_EVP_CIPHER_CTX_set_padding(
	          c,
	          pad );

	return( result );
}

/* Custom EVP_CipherInit_ex for testing error cases
 * Returns 1 if successful or 0 otherwise
 */
int EVP_CipherInit_ex(
     EVP_CIPHER_CTX *ctx,
     const EVP_CIPHER *type,
     ENGINE *impl,
     const unsigned char *key,
     const unsigned char *iv,
     int enc )
{
	int result = 0;

	if( caes_test_real_EVP_CipherInit_ex == NULL )
	{
		caes_test_real_EVP_CipherInit_ex = dlsym(
		                                    RTLD_NEXT,
		                                    "EVP_CipherInit_ex" );
	}
	if( caes_test_EVP_CipherInit_ex_attempts_before_fail == 0 )
	{
		caes_test_EVP_CipherInit_ex_attempts_before_fail = -1;

		return( 0 );
	}
	else if( caes_test_EVP_CipherInit_ex_attempts_before_fail > 0 )
	{
		caes_test_EVP_CipherInit_ex_attempts_before_fail--;
	}
	result = caes_test_real_EVP_CipherInit_ex(
	          ctx,
	          type,
	          impl,
	          key,
	          iv,
	          enc );

	return( result );
}

/* Custom EVP_CipherUpdate for testing error cases
 * Returns 1 if successful or 0 otherwise
 */
int EVP_CipherUpdate(
     EVP_CIPHER_CTX *ctx,
     unsigned char *out,
     int *outl,
     const unsigned char *in,
     int inl )
{
	int result = 0;

	if( caes_test_real_EVP_CipherUpdate == NULL )
	{
		caes_test_real_EVP_CipherUpdate = dlsym(
		                                   RTLD_NEXT,
		                                   "EVP_CipherUpdate" );
	}
	if( caes_test_EVP_CipherUpdate_attempts_before_fail == 0 )
	{
		caes_test_EVP_CipherUpdate_attempts_before_fail = -1;

		return( 0 );
	}
	else if( caes_test_EVP_CipherUpdate_attempts_before_fail > 0 )
	{
		caes_test_EVP_CipherUpdate_attempts_before_fail--;
	}
	result = caes_test_real_EVP_CipherUpdate(
	          ctx,
	          out,
	          outl,
	          in,
	          inl );

	return( result );
}

#endif /* defined( HAVE_LIBCRYPTO ) && defined( HAVE_OPENSSL_EVP_H ) && defined( HAVE_EVP_CRYPTO_AES_XTS ) */

#endif /* defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) */

