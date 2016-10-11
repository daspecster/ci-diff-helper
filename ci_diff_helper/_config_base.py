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

"""Base for configuration classes and associated helpers."""

import os

from ci_diff_helper import _utils
from ci_diff_helper import git_tools


_BRANCH_ERR_TEMPLATE = (
    'Build does not have an associated branch set (via %s).')


def _in_ci(env_var):
    """Detect if we are running in the target CI system.

    Assumes the only valid environment variable value is ``true``.

    :type env_var: str
    :param env_var: The environment variable which holds the status.

    :rtype: bool
    :returns: Flag indicating if we are running in the target CI system.
    """
    return os.getenv(env_var) == 'true'


def _ci_branch(env_var):
    """Get the current branch of CI build.

    :type env_var: str
    :param env_var: The environment variable which holds the branch.

    :rtype: str
    :returns: The name of the branch the current build is for / associated
              with. (May indicate the active branch or the base branch of
              a pull request.)
    :raises EnvironmentError: if the environment variable
                              isn't set during the build.
    """
    try:
        return os.environ[env_var]
    except KeyError as exc:
        msg = _BRANCH_ERR_TEMPLATE % (env_var,)
        raise EnvironmentError(exc, msg)


class Config(object):
    """Base class for caching CI configuration objects."""

    # Default instance attributes.
    _active = _utils.UNSET
    _branch = _utils.UNSET
    _is_merge = _utils.UNSET
    # Class attributes.
    _active_env_var = None
    _branch_env_var = None

    # pylint: disable=missing-returns-doc
    @property
    def active(self):
        """Indicates if currently running in the target CI system.

        :rtype: bool
        """
        if self._active is _utils.UNSET:
            self._active = _in_ci(self._active_env_var)
        return self._active

    @property
    def branch(self):
        """Indicates the current branch in the target CI system.

        This may indicate the active branch or the base branch of a
        pull request.

        :rtype: bool
        """
        if self._branch is _utils.UNSET:
            self._branch = _ci_branch(self._branch_env_var)
        return self._branch

    @property
    def is_merge(self):
        """Indicates if the HEAD commit is a merge commit.

        :rtype: bool
        """
        if self._is_merge is _utils.UNSET:
            self._is_merge = git_tools.merge_commit()
        return self._is_merge
    # pylint: enable=missing-returns-doc
