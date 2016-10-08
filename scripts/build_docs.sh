#!/bin/bash
#
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
#
# Build the oauth2client docs.

set -e

rm -rf docs/build/* docs/source/*
sphinx-apidoc \
  --separate --force \
  --output-dir docs/source \
  ci_diff_helper
# We only have one package, so modules.rst is overkill.
rm -f docs/source/modules.rst
# Manual edit for the root import.
echo "    :imported-members:" >> docs/source/ci_diff_helper.rst

# If anything has changed
if [[ -n "$(git diff -- docs/)" ]]; then
    echo "sphinx-apidoc generated changes that are not checked in to version control."
    exit 1
fi

sphinx-build -W \
  -b html \
  -d docs/build/doctrees \
  docs \
  docs/build/html
echo "Build finished. The HTML pages are in docs/build/html."
