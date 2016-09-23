from dulwich.diff_tree import tree_changes


class Calculator(object):

    @staticmethod
    def has_change_in_dirs(diffs, app_dirs):
        for dirs in app_dirs:
            for diff in diffs:
                if diff.startswith(dirs):
                    return True

        return False

    def calculate_ratio(self, diffs, app_dirs, test_dirs):
        tested_commmit_count = 0
        untested_commit_count = 0

        for diff in diffs:
            app_changes = self.has_change_in_dirs(diff, app_dirs)
            test_changes = self.has_change_in_dirs(diff, test_dirs)

            if app_changes and test_changes:
                tested_commmit_count += 1
            elif app_changes and not test_changes:
                untested_commit_count += 1

        total = untested_commit_count + tested_commmit_count

        return float(total - untested_commit_count) / float(total)

class Git(object):
    @staticmethod
    def get_commit_file_diffs(repo):

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
                this_commit_changes.append(x.old.path)

            commit_changes.append(this_commit_changes)

            prev = commit.tree
            cset = walker.next()

        return commit_changes
