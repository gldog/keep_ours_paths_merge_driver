import unittest

import keep_ours_paths_merge_driver.config as config


class TestConfigGetPAthWithPatterns(unittest.TestCase):

    def test_get_paths_with_patterns(self):
        from_environment_as_str = 'path-from-env1:pattern-from-env1'
        from_cl_args_as_list = None
        got = config.get_paths_with_patterns(from_environment_as_str, from_cl_args_as_list)
        expected = {'path-from-env1': 'pattern-from-env1'}
        self.assertEqual(expected, got)

        from_environment_as_str = 'path-from-env1:pattern-from-env1,path-from-env2:pattern-from-env2'
        from_cl_args_as_list = None
        got = config.get_paths_with_patterns(from_environment_as_str, from_cl_args_as_list)
        expected = {'path-from-env1': 'pattern-from-env1', 'path-from-env2': 'pattern-from-env2'}
        self.assertEqual(expected, got)

        from_environment_as_str = ',path-from-env1:pattern-from-env1,,path-from-env2:pattern-from-env2,'
        from_cl_args_as_list = None
        got = config.get_paths_with_patterns(from_environment_as_str, from_cl_args_as_list)
        expected = {'path-from-env1': 'pattern-from-env1', 'path-from-env2': 'pattern-from-env2'}
        self.assertEqual(expected, got)

        from_environment_as_str = ' path-from-env1:pattern-from-env1 , path-from-env2:pattern-from-env2 '
        from_cl_args_as_list = None
        got = config.get_paths_with_patterns(from_environment_as_str, from_cl_args_as_list)
        expected = {'path-from-env1': 'pattern-from-env1', 'path-from-env2': 'pattern-from-env2'}
        self.assertEqual(expected, got)

        # Switch defaults off by environment variable.
        from_environment_as_str = ''
        from_cl_args_as_list = None
        got = config.get_paths_with_patterns(from_environment_as_str, from_cl_args_as_list)
        expected = {}
        self.assertEqual(expected, got)

        # Switch defaults off by environment variable.
        from_environment_as_str = ''
        from_cl_args_as_list = ['path-from-cl1:pattern-from-cl1']
        got = config.get_paths_with_patterns(from_environment_as_str, from_cl_args_as_list)
        expected = {}
        self.assertEqual(expected, got)

        from_environment_as_str = None
        from_cl_args_as_list = ['path-from-cl1:pattern-from-cl1']
        got = config.get_paths_with_patterns(from_environment_as_str, from_cl_args_as_list)
        expected = {'path-from-cl1': 'pattern-from-cl1'}
        self.assertEqual(expected, got)

        from_environment_as_str = None
        from_cl_args_as_list = ['path-from-cl1:pattern-from-cl1', 'path-from-cl2:pattern-from-cl2']
        got = config.get_paths_with_patterns(from_environment_as_str, from_cl_args_as_list)
        expected = {'path-from-cl1': 'pattern-from-cl1', 'path-from-cl2': 'pattern-from-cl2'}
        self.assertEqual(expected, got)

        # Switch defaults off by command line.
        from_environment_as_str = None
        from_cl_args_as_list = ['']
        got = config.get_paths_with_patterns(from_environment_as_str, from_cl_args_as_list)
        expected = {}
        self.assertEqual(expected, got)

    def test_any(self):
        pass


if __name__ == '__main__':
    unittest.main()