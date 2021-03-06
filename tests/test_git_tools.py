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

import os
import unittest

from tests import utils


class Test_git_root(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.git_tools import git_root
        return git_root()

    def test_sys_call(self):
        import mock

        with mock.patch('ci_diff_helper._utils.check_output') as mocked:
            result = self._call_function_under_test()
            self.assertIs(result, mocked.return_value)
            mocked.assert_called_once_with(
                'git', 'rev-parse', '--show-toplevel')

    @unittest.skipUnless(utils.HAS_GIT, 'git not installed')
    def test_actual_call(self):
        result = self._call_function_under_test()
        result = os.path.abspath(result)  # Normalize path for Windows.
        tests_dir = os.path.dirname(__file__)
        root_dir = os.path.abspath(os.path.join(tests_dir, '..'))
        self.assertEqual(result, root_dir)


class Test_get_checked_in_files(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.git_tools import get_checked_in_files
        return get_checked_in_files()

    @staticmethod
    def _do_nothing(value):
        return value

    def test_it(self):
        import mock

        filenames = [
            'a.py',
            'shell-not-py.sh',
            os.path.join('b', 'c.py'),
            'Makefile',
            os.path.join('d', 'e', 'f.py'),
        ]
        cmd_output = '\n'.join(filenames)
        mock_output = mock.patch('ci_diff_helper._utils.check_output',
                                 return_value=cmd_output)

        git_root = os.path.join('totally', 'on', 'your', 'filesystem')
        mock_root = mock.patch('ci_diff_helper.git_tools.git_root',
                               return_value=git_root)

        mock_abspath = mock.patch('os.path.abspath', new=self._do_nothing)

        with mock_abspath:
            with mock_root:
                with mock_output as mocked:
                    result = self._call_function_under_test()
                    mocked.assert_called_once_with(
                        'git', 'ls-files', git_root)
                    self.assertEqual(result, filenames)

    @staticmethod
    def _all_files(root_dir):
        result = set()
        for dirname, _, filenames in os.walk(root_dir):
            for filename in filenames:
                result.add(os.path.join(dirname, filename))
        return result

    @unittest.skipUnless(utils.HAS_GIT, 'git not installed')
    def test_actual_call(self):
        result = self._call_function_under_test()
        tests_dir = os.path.dirname(__file__)
        root_dir = os.path.abspath(os.path.join(tests_dir, '..'))
        self.assertLessEqual(set(result), self._all_files(root_dir))


class Test_get_changed_files(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(blob_name1, blob_name2):
        from ci_diff_helper import git_tools

        return git_tools.get_changed_files(blob_name1, blob_name2)

    def _helper(self, changed, expected):
        import mock

        blob_name1 = 'HEAD'
        blob_name2 = '031cf739bc419eb2c320f8c897b03c04796943a9'
        output_patch = mock.patch('ci_diff_helper._utils.check_output',
                                  return_value=changed)
        with output_patch as mocked:
            result = self._call_function_under_test(blob_name1, blob_name2)
            self.assertEqual(result, expected)
            mocked.assert_called_once_with(
                'git', 'diff', '--name-only', blob_name1, blob_name2)

    def test_empty(self):
        self._helper('', [])

    def test_with_changes(self):
        expected = ['foo.py', os.path.join('bar', 'baz.txt')]
        self._helper('\n'.join(expected), expected)

    @unittest.skipUnless(utils.HAS_GIT, 'git not installed')
    def test_actual_call_same(self):
        blob_name1 = '7575455ec442498f3d1c5b2a8d3bc7861918d987'
        blob_name2 = blob_name1
        result = self._call_function_under_test(blob_name1, blob_name2)
        expected = []
        self.assertEqual(result, expected)

    def _maybe_skip_if_no_commit(self, blob_name):
        from ci_diff_helper import _utils

        commit_file = _utils.check_output(
            'git', 'cat-file', '-t', blob_name, ignore_err=True)
        if commit_file != 'commit':  # pragma: NO COVER
            self.skipTest(
                'Commit {!r} does not exist'.format(blob_name))

    @unittest.skipUnless(utils.HAS_GIT, 'git not installed')
    def test_actual_call_parent(self):  # pragma: NO COVER
        blob_name1 = 'bdb1ee24f05abe80f099bc5fd612fd46b36f3b28'
        self._maybe_skip_if_no_commit(blob_name1)
        blob_name2 = blob_name1 + '^'
        self._maybe_skip_if_no_commit(blob_name2)

        result = self._call_function_under_test(blob_name1, blob_name2)
        expected = [
            'ci_diff_helper/appveyor.py',
            'ci_diff_helper/environment_vars.py',
            'docs/ci_diff_helper.appveyor.rst',
            'docs/index.rst',
            'tests/test_appveyor.py',
            'tests/test_travis.py',
        ]
        self.assertEqual(result, expected)


class Test_merge_commit(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(revision):
        from ci_diff_helper.git_tools import merge_commit
        return merge_commit(revision)

    def _helper(self, parents, revision='HEAD'):
        import mock

        output_patch = mock.patch('ci_diff_helper._utils.check_output',
                                  return_value=parents)
        with output_patch as mocked:
            result = self._call_function_under_test(revision)
            mocked.assert_called_once_with(
                'git', 'log', '--pretty=%P', '-1', revision)
            return result

    def test_non_merge_default(self):
        parents = 'fd5cffa5d437607159ceeda68895b9b53f23a531'
        result = self._helper(parents)
        self.assertFalse(result)

    def test_non_merge_explicit(self):
        parents = 'fd5cffa5d437607159ceeda68895b9b53f23a531'
        result = self._helper(parents, revision='master')
        self.assertFalse(result)

    def test_merge(self):
        parents = ('47ebd0bb461180dcab674b3beca5ec9c11a1b976 '
                   'e8fd7135497b1027cba26ffab7851f1533ff08e3')
        result = self._helper(parents)
        self.assertTrue(result)

    def test_three_parents(self):
        parents = ('8103a3b85aa5f3e2b14200bfef815539c1be109a '
                   'e9b5c87f8153fd177a0e10f7abda0b4bb4730626 '
                   'ce60976326725217c16fe84b5120c6a8661177a8')
        with self.assertRaises(NotImplementedError):
            self._helper(parents)


class Test_commit_subject(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(*args):
        from ci_diff_helper.git_tools import commit_subject
        return commit_subject(*args)

    def test_non_merge_default(self):
        import mock

        output_patch = mock.patch('ci_diff_helper._utils.check_output')
        with output_patch as mocked:
            result = self._call_function_under_test()
            self.assertIs(result, mocked.return_value)
            mocked.assert_called_once_with(
                'git', 'log', '--pretty=%s', '-1', 'HEAD')

    def test_non_merge_explicit(self):
        import mock
        revision = 'ffe035e3c4b4d11053b6162fce96474bb15c6869'

        output_patch = mock.patch('ci_diff_helper._utils.check_output')
        with output_patch as mocked:
            result = self._call_function_under_test(revision)
            self.assertIs(result, mocked.return_value)
            mocked.assert_called_once_with(
                'git', 'log', '--pretty=%s', '-1', revision)
