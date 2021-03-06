# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Custom script to run pycodestyle on ci-diff-helper codebase.

This runs pycodestyle as a script via subprocess but only runs it on the
.py files that are checked in to the repository.
"""


from __future__ import print_function

import os
import subprocess
import sys

import ci_diff_helper


def main(all_files=None):
    """Run pycodestyle on all Python files in the repository.

    Args:
        all_files (Optional[list]): A list of all files to consider.
    """
    if all_files is None:
        all_files = ci_diff_helper.get_checked_in_files()

    python_files = []
    for filename in all_files:
        _, ext = os.path.splitext(filename)
        if ext == '.py':
            python_files.append(filename)

    if not python_files:
        print('No Python files to lint, exiting.')
    else:
        pycodestyle_command = ['pycodestyle'] + python_files
        status_code = subprocess.call(pycodestyle_command)
        if status_code != 0:
            sys.exit(status_code)


if __name__ == '__main__':
    main()
