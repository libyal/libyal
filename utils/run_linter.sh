#!/bin/bash
# -*- coding: utf-8 -*-
#
# Script to run pylint on changed files.
#
# Copyright (c) 2013-2015, Joachim Metz <joachim.metz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

EXIT_FAILURE=1;
EXIT_SUCCESS=0;

PYLINT=`which pylint`;

if ! test -x ${PYLINT};
then
	echo "Missing executable: ${PYLINT}";

	exit ${EXIT_FAILURE};
fi

# Examples of the output of "git status -s"
# If a file is added:
# A utils/common.sh
# If a file is modified:
# M utils/common.sh
# If a file is renamed:
# R utils/common.sh -> utils/uncommon.sh
# If a file is modified and renamed:
# RM utils/common.sh -> utils/uncommon.sh
AWK_SCRIPT="if (\$1 == \"A\" || \$1 == \"AM\" || \$1 == \"M\" || \$1 == \"MM\") { print \$2; } else if (\$1 == \"R\" || \$1 == \"RM\") { print \$4; }";

# First find all files that need to be run against the pylint.
FILES=`git status -s | grep -v "^?" | awk "{ ${AWK_SCRIPT} }" | grep "\.py$"`;

echo "Running pylint on changed files.";

for FILE in ${FILES};
do
  if test "${FILE}" = "setup.py";
  then
    echo "Skipping: ${FILE}";
    continue;
  fi

  echo "Checking: ${FILE}";
  ${PYLINT} --rcfile=utils/pylintrc "${FILE}";

  if test $? -ne 0;
  then
    exit ${EXIT_FAILURE};
  fi
done

exit ${EXIT_SUCCESS};

