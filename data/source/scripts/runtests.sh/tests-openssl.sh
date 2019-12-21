# Test "./configure && make && make check" with fallback crypto implementation.

run_configure_make_check "--with-openssl=no";
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

# Test "./configure && make && make check" with OpenSSL non-EVP implementation.

run_configure_make_check "--enable-openssl-evp-cipher=no --enable-openssl-evp-md=no";
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

# Test "./configure && make && make check" with OpenSSL EVP implementation.

run_configure_make_check "--enable-openssl-evp-cipher=yes --enable-openssl-evp-md=yes";
RESULT=$$?;

if test $${RESULT} -ne $${EXIT_SUCCESS};
then
	exit $${EXIT_FAILURE};
fi

