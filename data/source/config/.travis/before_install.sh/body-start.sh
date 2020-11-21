#!/bin/sh
# Script to run before_install step on Travis-CI
#
# Version: 20201121

# Exit on error.
set -e;

sudo apt-get update;
sudo apt-mark hold openssh-server postgresql-12;
sudo apt-get --fix-missing -o Dpkg::Options::="--force-confold" upgrade -y --allow-unauthenticated;

sudo apt-get install -y ${dpkg_build_dependencies};
