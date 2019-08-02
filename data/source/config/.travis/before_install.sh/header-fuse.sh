#!/bin/bash
# Script to run before_install step on Travis-CI
#
# Version: 20190802

# Exit on error.
set -e;

if test $${TRAVIS_OS_NAME} = "linux" || test $${TRAVIS_OS_NAME} = "linux-ppc64le";
then
	sudo apt-get update;
	sudo apt-mark hold mysql-server-5.7;
	sudo apt-get --fix-missing -o Dpkg::Options::="--force-confold" upgrade -y --allow-unauthenticated;

	sudo apt-get install -y ${dpkg_build_dependencies};

elif test $${TRAVIS_OS_NAME} = "osx";
then
	brew update

	brew install gettext gnu-sed;
	brew link --force gettext;

	brew tap homebrew/cask;
	brew cask install osxfuse;
fi

