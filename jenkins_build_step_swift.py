import json
import os
from subprocess import Popen, PIPE

from conf import base_api_link, base_build_status_link, user, passwd
from jbi_logger import log
from pull_request_file_comments import SendResultsToPullRequestFiles
from pull_request_main_comments_section import PullRequestCommits


def execute_linux_command(cmd):
    log('Executing command {}'.format(cmd))
    proc = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
    out, err = proc.communicate()
    code = proc.returncode
    log('Command code"{0}, result"{1}, error:{2}'.format(code, out, err))
    if code != 0:
        return code, err
    elif code == 0:
        return code, out


def send_file_results(file, tailor_count):
    log('Sending results for file {}.'.format(file))
    file_comments = SendResultsToPullRequestFiles(
        base_api_link=base_api_link,
        checked_file=file,
        username=user,
        passwd=passwd
    )
    file_comments.send_static_check_results_swift(tailor_count)
    log('Sending results finished. Output: {}'.format(file_comments))


def static_check(file_to_check, cmd, result_file):
    code, result = execute_linux_command(cmd)

    if code != 0:
        count = 'Error while executing static check: {}'.format(result)
    else:
        log('Trying to count errors in file {}'.format(result_file))
        report = json.loads(result_file)
        summary = report['summary']

    return count


def commit_files_handler(commit_id):
    cmd = 'git diff-tree --no-commit-id --name-only -r {}'.format(commit_id)
    code, out = execute_linux_command(cmd)
    log('List of files changed in commit received: {}'.format(out))
    files = [file for file in out.split('\n')]
    for file in files:
        if not file or '.swift' not in file:
            continue
        log('Checking file {}'.format(file))
        tailor_file = "tailor_{0}.json".format(file)
        cmd = '/usr/local/bin/tailor -f json {0} > {1}'.format(file, tailor_file)

        tailor_count = static_check(file, cmd, tailor_file)
        log('Tailor count for file {0}: {1}'.format(file, tailor_count))

        send_file_results(file, tailor_count)


def main():
    pr = PullRequestCommits(
        base_api_link=base_api_link,
        username=user,
        passwd=passwd
    )
    commit_list = pr.get_commits()
    log('List of commits for pull request received: {}'.format(commit_list))

    for commit_id in commit_list:
        log('Processing commit ID {}'.format(commit_id))
        commit_files_handler(commit_id)


if __name__ == '__main__':
    main()
