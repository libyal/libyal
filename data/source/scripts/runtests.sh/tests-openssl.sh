# Test "./configure && make && make check" with fallback crypto implementation.

run_configure_make_check "--with-openssl=no";
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

# Test "./configure && make && make check" with OpenSSL non-EVP implementation.

run_configure_make_check "--disable-openssl-evp-cipher --disable-openssl-evp-md";
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

# Test "./configure && make && make check" with OpenSSL EVP implementation.

run_configure_make_check "--enable-openssl-evp-cipher --enable-openssl-evp-md";
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

