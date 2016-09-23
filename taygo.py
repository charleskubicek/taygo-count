import argparse
import calendar
import os
import sys
import subprocess
import itertools
import time
from datetime import datetime, date, time
import json


def call_and_get_output(command, quiet=True):
    lines = []
    if not quiet: print "calling: '" + command + "' from: '" + os.getcwd() + "'"
    ps_command = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = ps_command.stdout.readline()
        if line != '':
            lines.append(line)
        else:
            break

    return lines


def verbose(message):
    if args.verbose:
        print message


def out(message):
    if not args.quiet:
        print message


def quiet(message):
    if args.quiet:
        print message


parser = argparse.ArgumentParser(description='show ratio between application code and test code in commits')
parser.add_argument('-v', '--verbose', action='store_true', help='Print debug output')
parser.add_argument('-q', '--quiet', action='store_true', help='show only percent')
parser.add_argument('repo', type=str, help='git repository to scan')
args = parser.parse_args()
repo = args.repo

out('repo: ' + repo)

branch = 'master'

code_dirs = ["app/", "src/"]
test_dirs = ["test/", "features/", "/it", "/cdc"]
ignored = ["/project"]


class AnalysisResult(object):
    def __init__(self, repo, commit_count=0, code_only_count=0, test_only_count=0, both_count=0, days_since_last_commit=-1):
        self.repo = repo
        self.commit_count = commit_count
        self.code_only_count = code_only_count
        self.test_only_count = test_only_count
        self.both_count = both_count
        self.days_since_last_commit = days_since_last_commit


def is_test_file(filename):
    return len(filter(lambda td: filename.startswith(td), test_dirs)) > 0


def contains_test_file(filenames):
    return len(filter(lambda fn: is_test_file(fn), filenames)) > 0


def is_in_code_dir(filename):
    return len(filter(lambda cd: filename.startswith(cd), code_dirs)) > 0


def timestamp_of_last_code_commit(commits):
    for c in reversed(commits):
        files = call_and_get_output('git -C \"{0}\" show --pretty="format:" --name-only '.format(repo) + c.strip())
        if contains_test_file(files):
            return int(call_and_get_output('git -C \"{0}\" show -s --format=%ct '.format(repo) + c.strip())[0])

    return 0


def is_within_one_month(timestamp):
    return (datetime.now() - datetime.fromtimestamp(timestamp)).days < 30

def analyse_repo(repo):
    commits = call_and_get_output("git -C \"{0}\" rev-list --all --reverse --no-merges".format(repo))
    commits_in_repo = len(commits)
    last_commit_timestamp = timestamp_of_last_code_commit(commits)
    days_since_last_commit = (datetime.now() - datetime.fromtimestamp(last_commit_timestamp)).days
    #out('days since last commit: ' + str(days_since_last_commit))
    #out('commits to process: ' + str(commits_in_repo))

    result = AnalysisResult(repo = repo, days_since_last_commit=days_since_last_commit)

    for w in commits:
        verbose('commit ' + w)

        has_code = False
        has_tests = False

        files = call_and_get_output('git -C \"{0}\" show --pretty="format:" --name-only '.format(repo) + w.strip())

        for f in map(str.strip, files):
            verbose('  ' + f)
            if is_in_code_dir(f):
                has_code = True
            elif is_test_file(f):
                has_tests = True

        result.commit_count += 1
        # print 'processing commits: {0} \r'.format(str(commit_count))

        if has_code and has_tests:
            result.both_count += 1
        elif has_code and not has_tests:
            result.code_only_count += 1
        elif not has_code and has_tests:
            result.test_only_count += 1

    return result


def output_result(result):
    if result.code_only_count + result.both_count > 0:
        ratio = float(result.both_count) / (float(result.code_only_count + result.both_count))

        print json.dumps({
            'repo_name' : result.repo,
            'days_since_last_commit': result.days_since_last_commit,
            'commit_count': result.commit_count,
            'ratio': round(ratio, 2)})
    else:
        print json.dumps({
            'repo_name' : result.repo,
            'days_since_last_commit': result.days_since_last_commit,
            'commit_count': result.commit_count,
            'ratio': 0.0})


output_result(analyse_repo(repo))
