#! /usr/bin/env python

import time
import unittest

from dulwich.repo import Repo
from os import mkdir
from taygo.taygo import *


class TaygoTests(unittest.TestCase):

    calc = Calculator()
    git = Git()

    def commit_files(self, repo, *paths):

        for path in paths:
            open(repo.path + '/' + path, 'wb').write(b"monty")
            repo.stage([path])

        return repo.do_commit(b"A commit of %s and maybe others" % paths[0], committer=b"Charles <charles@test.org>")

    def test_should_return_diffs_from_git_repo(self):
        repo_dir = '/var/tmp/myrepo' + str(time.time() * 1000.0)
        mkdir(repo_dir)
        mkdir(repo_dir + '/test')
        mkdir(repo_dir + '/src')
        repo = Repo.init(repo_dir)

        self.commit_files(repo, 'readme.md')
        self.commit_files(repo, '.git_ignore')
        self.commit_files(repo, 'src/foo', 'test/foo_test')

        diffs = self.git.get_commit_file_diffs(repo)
        self.assertListEqual(diffs, [['src/foo', 'test/foo_test'], ['.git_ignore']])

    def test_should_calcualte_ratios(self):
        self.assertEqual(1.0, self.calc.calculate_ratio([['readme.md'], ['src/foo', 'test/foo_test']], ['src'], ['test']))

    def test_should_find_app_change(self):
        self.assertTrue(self.calc.has_change_in_dirs(['src/foo'], ['src']))
        self.assertFalse(self.calc.has_change_in_dirs(['test/foo_test'], ['src']))

    def test_should_find_test_change(self):
        self.assertTrue(self.calc.has_change_in_dirs(['test/foo_test'], ['test']))
        self.assertFalse(self.calc.has_change_in_dirs(['src/foo'], ['test']))