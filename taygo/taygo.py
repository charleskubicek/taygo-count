from dulwich.diff_tree import tree_changes
from dulwich.repo import Repo
import argparse
import sys


class Calculator(object):
    @staticmethod
    def has_change_in_dirs(diffs, app_dirs):
        for dirs in app_dirs:
            for diff in diffs:
                if diff.startswith(dirs):
                    return True

        return False

    def calculate_ratio(self, diffs, app_dirs, test_dirs):
        # print diffs
        tested_commit_count = 0
        untested_commit_count = 0

        for diff in diffs:
            app_changes = self.has_change_in_dirs(diff, app_dirs)
            test_changes = self.has_change_in_dirs(diff, test_dirs)

            if app_changes and test_changes:
                tested_commit_count += 1
            elif app_changes and not test_changes:
                untested_commit_count += 1

        total = untested_commit_count + tested_commit_count

        if total == 0:
            return float('nan')
        else:
            return float(total - untested_commit_count) / float(total)


class Git(object):
    @staticmethod
    def get_commit_file_diffs(repo_path, max_commit_count=-1):
        repo = Repo(repo_path)
        prev = None
        walker = repo.get_graph_walker()

        commit_changes = []
        commit_count = 0

        cset = walker.next()
        while cset is not None:
            commit = repo.get_object(cset)
            if prev is None:
                prev = commit.tree
                cset = walker.next()
                continue

            this_commit_changes = []

            for x in tree_changes(repo, prev, commit.tree):
                if x.old.path is not None:
                    this_commit_changes.append(x.old.path)

            commit_changes.append(this_commit_changes)

            prev = commit.tree

            commit_count += 1

            if max_commit_count > 0 and commit_count >= max_commit_count:
                cset = None
            else:
                cset = walker.next()

        return RepoDiffResult(repo_path, commit_changes, commit_count)


class RepoDiffResult(object):
    def __init__(self, repo, commit_changes, commit_count=0):
        self.repo = repo
        self.commit_changes = commit_changes
        self.commit_count = commit_count


class ArgParser(object):
    @staticmethod
    def get_args(args):
        parser = argparse.ArgumentParser(description='show ratio between application code and test code in commits')
        parser.add_argument('-c', '--commit_count', type=int,
                            help='the maximum number of commits to count, counted backwards from most recent')
        parser.add_argument('repo', type=str, help='git repository to scan')
        return parser.parse_args(args)


if __name__ == '__main__':
    args = ArgParser().get_args(sys.argv[1:])
    repo = args.repo

    app_dirs = ['api/src/main/java']
    test_dirs = ['api/src/test/java']

    commits = Git().get_commit_file_diffs(repo, max_commit_count=int(args.commit_count))
    ratio = Calculator().calculate_ratio(commits.commit_changes, app_dirs, test_dirs)

    print "%s from %s commits" % (str(ratio), str(commits.commit_count))
