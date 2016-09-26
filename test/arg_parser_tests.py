import unittest

from taygo.taygo import *


class ArgParserTests(unittest.TestCase):

    def test_should_fail_wihout_repo(self):
        with self.assertRaises(SystemExit) as cm:
            ArgParser().get_args([])

        self.assertEqual(cm.exception.code, 2)

    def test_should_parse_commit_count(self):
        self.assertEqual(10, ArgParser().get_args(['--commit_count', '10', 'repo']).commit_count)
