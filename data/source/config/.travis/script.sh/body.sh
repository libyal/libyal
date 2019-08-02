#!/bin/bash
# Script to run script step on Travis-CI
#
# Version: 20190802

# Exit on error.
set -e;

if test $${TRAVIS_OS_NAME} = "linux" || test $${TRAVIS_OS_NAME} = "linux-ppc64le";
then
	export PATH=$$(echo $$PATH | tr ":" "\n" | sed '/\/opt\/python/d' | tr "\n" ":" | sed "s/::/:/g");
fi

if test $${TARGET} != "coverity";
then
	set +e;

	./configure $${CONFIGURE_OPTIONS};
	RESULT=$$?;

	if test $${RESULT} -eq 0;
	then
		make > /dev/null;
		RESULT=$$?;
	fi
	if test $${RESULT} -eq 0;
	then
		make check CHECK_WITH_STDERR=1;
		RESULT=$$?;
	fi
	if test $${RESULT} -ne 0;
	then
	        if test -f tests/test-suite.log;
		then
			cat tests/test-suite.log;
		fi
		return $${RESULT};
	fi

	set -e;

	if test $${TARGET} = "macos-gcc-pkgbuild";
	then
		export VERSION=`sed '5!d; s/^ \[//;s/\],$$//' configure.ac`;

		make install DESTDIR=$${PWD}/osx-pkg;
		mkdir -p $${PWD}/osx-pkg/usr/share/doc/libcerror;
		cp AUTHORS COPYING NEWS README $${PWD}/osx-pkg/usr/share/doc/libcerror;

		pkgbuild --root osx-pkg --identifier com.github.libyal.libcerror --version $${VERSION} --ownership recommended ../libcerror-$${VERSION}.pkg;
	fi
fi

