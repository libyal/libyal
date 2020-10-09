#!/bin/sh
# Script to run before_install step on Travis-CI
#
# Version: 20201009

# Exit on error.
set -e;

if test $${TRAVIS_OS_NAME} = "linux";
then
	sudo apt-get update;
	sudo apt-mark hold openssh-server;
	sudo apt-get --fix-missing -o Dpkg::Options::="--force-confold" upgrade -y --allow-unauthenticated;

	sudo apt-get install -y ${dpkg_build_dependencies};

elif test $${TRAVIS_OS_NAME} = "osx";
then
	# Prevent from the 30 days autoclean being triggered on install.
	export HOMEBREW_NO_INSTALL_CLEANUP=1;

	brew update;

	brew install gettext gnu-sed;
