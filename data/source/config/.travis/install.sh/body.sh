#!/bin/bash
# Script to run install step on Travis-CI
#
# Version: 20190802

# Exit on error.
set -e;

if test $${TARGET} = "docker";
then
	CONTAINER_NAME="testcontainer";
	CONTAINER_OPTIONS="-e LANG=en_US.UTF-8";

	docker cp ../${library_name} $${CONTAINER_NAME}:/

	# Note that exec options need to be defined before the container name.
	docker exec $${CONTAINER_OPTIONS} $${CONTAINER_NAME} sh -c "cd ${library_name} && ./synclibs.sh --use-head && ./autogen.sh";

else
	if test $${TRAVIS_OS_NAME} = "osx";
	then
		export SED="/usr/local/bin/gsed";
	fi

	./synclibs.sh --use-head;
	./autogen.sh;

	if test $${TARGET} = "linux-gcc-shared" || test $${TARGET} = "linux-gcc-shared-wide-character-type";
	then
		./configure > /dev/null;
		make > /dev/null;

		./syncsharedlibs.sh --use-head;
	fi

	if test -x "synctestdata.sh";
	then
		./synctestdata.sh;
	fi
fi

