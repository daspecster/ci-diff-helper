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

import unittest


class Test__in_travis(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _in_travis
        return _in_travis()

    def test_success(self):
        import mock
        from ci_diff_helper import travis

        mock_env = {travis._IN_TRAVIS_ENV: 'true'}
        with mock.patch('os.environ', new=mock_env):
            self.assertTrue(self._call_function_under_test())

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            self.assertFalse(self._call_function_under_test())


class Test__travis_pr(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _travis_pr
        return _travis_pr()

    def test_success(self):
        import mock
        from ci_diff_helper import travis

        valid_int = '1234'
        actual_val = 1234
        self.assertEqual(int(valid_int), actual_val)
        mock_env = {travis._PR_ENV: valid_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertEqual(self._call_function_under_test(), actual_val)

    def test_failure_unset(self):
        import mock

        with mock.patch('os.environ', new={}):
            self.assertIsNone(self._call_function_under_test())

    def test_failure_bad_value(self):
        import mock
        from ci_diff_helper import travis

        not_int = 'not-int'
        self.assertRaises(ValueError, int, not_int)
        mock_env = {travis._PR_ENV: not_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertIsNone(self._call_function_under_test())


class Test__travis_branch(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _travis_branch
        return _travis_branch()

    def test_success(self):
        import mock
        from ci_diff_helper import travis

        branch = 'this-very-branch'
        mock_env = {travis._BRANCH_ENV: branch}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertEqual(result, branch)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                self._call_function_under_test()


class Test__travis_event_type(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _travis_event_type
        return _travis_event_type()

    def test_success(self):
        import mock
        from ci_diff_helper import travis

        event_env = 'push'
        mock_env = {travis._EVENT_TYPE_ENV: event_env}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertIs(result, travis.TravisEventType.push)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(ValueError):
                self._call_function_under_test()


class Test__push_build_base(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _push_build_base
        return _push_build_base()

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                self._call_function_under_test()

    def test_unresolved_start_commit(self):
        import mock
        from ci_diff_helper import travis

        start = 'a'
        commit_range = start + travis._RANGE_DELIMITER + 'b'
        mock_env = {travis._RANGE_ENV: commit_range}
        with mock.patch('os.environ', new=mock_env):
            # Make sure the start commit doesn't resolve.
            output_mock = mock.patch('ci_diff_helper._utils.check_output',
                                     return_value=None)
            with output_mock as mocked:
                with self.assertRaises(NotImplementedError):
                    self._call_function_under_test()
                mocked.assert_called_once_with(
                    'git', 'rev-parse', start, ignore_err=True)

    def _merge_base_helper(self, start_full, merge_base):
        import mock
        from ci_diff_helper import travis

        # Make a patch for os.environ to pass through the range.
        start = 'a'
        finish = 'b'
        commit_range = start + travis._RANGE_DELIMITER + finish
        mock_env = {travis._RANGE_ENV: commit_range}
        env_patch = mock.patch('os.environ', new=mock_env)
        # Make a patch for the system calls (check_output). Use
        # side_effect=[...] to support multiple calls getting
        # different return values.
        output_mock = mock.patch('ci_diff_helper._utils.check_output',
                                 side_effect=[start_full, merge_base])
        with env_patch:
            with output_mock as mocked:
                if start_full == merge_base:
                    result = self._call_function_under_test()
                    self.assertEqual(result, merge_base)
                else:
                    with self.assertRaises(ValueError):
                        self._call_function_under_test()

                self.assertEqual(mocked.call_count, 2)
                mocked.assert_any_call(
                    'git', 'rev-parse', start, ignore_err=True)
                mocked.assert_any_call(
                    'git', 'merge-base', start_full, finish, ignore_err=True)

    def test_bad_merge(self):
        start_full = 'abcd'
        merge_base = 'not-abcd'
        self.assertNotEqual(start_full, merge_base)
        self._merge_base_helper(start_full, merge_base)

    def test_success(self):
        start_full = 'abcd'
        merge_base = start_full
        self._merge_base_helper(start_full, merge_base)


class TravisEventType(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from ci_diff_helper import travis
        return travis.TravisEventType

    def _make_one(self, enum_val):
        klass = self._get_target_class()
        return klass(enum_val)

    def test_members(self):
        klass = self._get_target_class()
        self.assertEqual(set(klass.__members__.keys()),
                         set(['api', 'cron', 'pull_request', 'push']))

    def test_api(self):
        klass = self._get_target_class()
        enum_obj = self._make_one('api')
        self.assertIs(enum_obj, klass.api)

    def test_cron(self):
        klass = self._get_target_class()
        enum_obj = self._make_one('cron')
        self.assertIs(enum_obj, klass.cron)

    def test_pull_request(self):
        klass = self._get_target_class()
        enum_obj = self._make_one('pull_request')
        self.assertIs(enum_obj, klass.pull_request)

    def test_push(self):
        klass = self._get_target_class()
        enum_obj = self._make_one('push')
        self.assertIs(enum_obj, klass.push)


class TestTravis(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from ci_diff_helper import travis
        return travis.Travis

    def _make_one(self):
        klass = self._get_target_class()
        return klass()

    def test_constructor(self):
        from ci_diff_helper import travis

        klass = self._get_target_class()
        config = self._make_one()
        self.assertIsInstance(config, klass)
        self.assertIs(config._active, travis._UNSET)
        self.assertIs(config._pr, travis._UNSET)

    def _active_helper(self, active_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _active value set.
        self.assertIs(config._active, travis._UNSET)

        # Patch the helper so we can control the value.
        in_travis_patch = mock.patch(
            'ci_diff_helper.travis._in_travis', return_value=active_val)
        with in_travis_patch as mocked:
            result = config.active
            self.assertIs(result, active_val)
            mocked.assert_called_once_with()

        return config

    def test_active_property(self):
        active_val = object()
        self._active_helper(active_val)

    def test_active_property_cache(self):
        active_val = object()
        config = self._active_helper(active_val)
        # Test that the value is cached.
        self.assertIs(config._active, active_val)
        # Test that cached value is re-used.
        self.assertIs(config.active, active_val)

    def _pr_helper(self, pr_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _pr value set.
        self.assertIs(config._pr, travis._UNSET)

        # Patch the helper so we can control the value.
        travis_pr_patch = mock.patch(
            'ci_diff_helper.travis._travis_pr', return_value=pr_val)
        with travis_pr_patch as mocked:
            result = config.pr
            self.assertIs(result, pr_val)
            mocked.assert_called_once_with()

        return config

    def test_pr_property(self):
        pr_val = 1337
        self._pr_helper(pr_val)

    def test_pr_property_cache(self):
        pr_val = 42
        config = self._pr_helper(pr_val)
        # Test that the value is cached.
        self.assertIs(config._pr, pr_val)
        # Test that cached value is re-used.
        self.assertIs(config.pr, pr_val)

    def _branch_helper(self, branch_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _branch value set.
        self.assertIs(config._branch, travis._UNSET)

        # Patch the helper so we can control the value.
        in_travis_patch = mock.patch(
            'ci_diff_helper.travis._travis_branch',
            return_value=branch_val)
        with in_travis_patch as mocked:
            result = config.branch
            self.assertIs(result, branch_val)
            mocked.assert_called_once_with()

        return config

    def test_branch_property(self):
        branch_val = 'branch-on-a-tree-in-a-forest'
        self._branch_helper(branch_val)

    def test_branch_property_cache(self):
        branch_val = 'make-tomorrow-a-tree'
        config = self._branch_helper(branch_val)
        # Test that the value is cached.
        self.assertIs(config._branch, branch_val)
        # Test that cached value is re-used.
        self.assertIs(config.branch, branch_val)

    def test_branch_property_error(self):
        import mock

        config = self._make_one()
        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                config.branch

    def test_base_property_in_pr(self):
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure the Travis config thinks we are in a PR.
        config._event_type = travis.TravisEventType.pull_request
        self.assertTrue(config.in_pr)
        # Make sure the Travis config knows the current branch.
        branch = 'scary-tree-branch'
        config._branch = branch
        self.assertEqual(config.branch, branch)
        # Check that in the PR case, the base is a branch.
        self.assertIs(config._base, travis._UNSET)
        self.assertEqual(config.base, branch)
        # Verify that caching works.
        self.assertEqual(config._base, branch)
        self.assertEqual(config.base, branch)

    def test_base_property_push(self):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure the Travis config thinks we are in a push build.
        config._event_type = travis.TravisEventType.push
        self.assertFalse(config.in_pr)
        self.assertIs(config.event_type, travis.TravisEventType.push)
        # Check that in the "push" case, the base gets set
        # from _push_build_base().
        base_val = '076879d777af62e621c9f72d2b5f6863e88689e9'
        push_base_patch = mock.patch(
            'ci_diff_helper.travis._push_build_base',
            return_value=base_val)
        self.assertIs(config._base, travis._UNSET)
        with push_base_patch as mocked:
            self.assertEqual(config.base, base_val)
            mocked.assert_called_once_with()
        # Verify that caching works.
        self.assertEqual(config._base, base_val)
        self.assertEqual(config.base, base_val)

    def test_base_property_non_pr_or_push(self):
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure the Travis config thinks we are not in a PR.
        config._event_type = travis.TravisEventType.cron
        self.assertFalse(config.in_pr)
        # Verify the failure.
        with self.assertRaises(NotImplementedError):
            config.base

    def _event_type_helper(self, event_type_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _event_type value set.
        self.assertIs(config._event_type, travis._UNSET)

        # Patch the helper so we can control the value.
        in_travis_patch = mock.patch(
            'ci_diff_helper.travis._travis_event_type',
            return_value=event_type_val)
        with in_travis_patch as mocked:
            result = config.event_type
            self.assertIs(result, event_type_val)
            mocked.assert_called_once_with()

        return config

    def test_event_type_property(self):
        event_type_val = 'push'
        self._event_type_helper(event_type_val)

    def test_event_type_property_cache(self):
        event_type_val = 'cron'
        config = self._event_type_helper(event_type_val)
        # Test that the value is cached.
        self.assertIs(config._event_type, event_type_val)
        # Test that cached value is re-used.
        self.assertIs(config.event_type, event_type_val)