from dulwich.diff_tree import tree_changes
from dulwich.repo import Repo
import argparse


class Calculator(object):
    @staticmethod
    def has_change_in_dirs(diffs, app_dirs):
        for dirs in app_dirs:
            for diff in diffs:
                if diff.startswith(dirs):
                    return True

        return False

    def calculate_ratio(self, diffs, app_dirs, test_dirs):
        print diffs
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

        return float(total - untested_commit_count) / float(total)


class Git(object):
    @staticmethod
    def get_commit_file_diffs(repo_path):
        repo = Repo(repo_path)
        prev = None
        walker = repo.get_graph_walker()

        commit_changes = []

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
            cset = walker.next()

        return commit_changes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='show ratio between application code and test code in commits')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print debug output')
    parser.add_argument('-q', '--quiet', action='store_true', help='show only percent')
    parser.add_argument('repo', type=str, help='git repository to scan')
    args = parser.parse_args()
    repo = args.repo

    app_dirs = ['taygo']
    test_dirs = ['test']

    ratio = Calculator().calculate_ratio(Git().get_commit_file_diffs(repo), app_dirs, test_dirs)
    print(str(ratio))
