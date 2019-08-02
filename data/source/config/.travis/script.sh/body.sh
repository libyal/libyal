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

if test $${TARGET} = "docker";
then
	CONTAINER_NAME="testcontainer";
	CONTAINER_OPTIONS="-e LANG=en_US.UTF-8";

	# Note that exec options need to be defined before the container name.
	docker exec $${CONTAINER_OPTIONS} $${CONTAINER_NAME} sh -c "cd ${library_name} && .travis/runtests.sh";

elif test $${TARGET} != "coverity";
then
	.travis/runtests.sh;

	if test $${TARGET} = "macos-gcc-pkgbuild";
	then
		export VERSION=`sed '5!d; s/^ \[//;s/\],$$//' configure.ac`;

		make install DESTDIR=$${PWD}/osx-pkg;
		mkdir -p $${PWD}/osx-pkg/usr/share/doc/${library_name};
		cp AUTHORS COPYING NEWS README $${PWD}/osx-pkg/usr/share/doc/${library_name};

		pkgbuild --root osx-pkg --identifier com.github.libyal.${library_name} --version $${VERSION} --ownership recommended ../${library_name}-$${VERSION}.pkg;
	fi
fi

