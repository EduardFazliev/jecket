import json
import os
from subprocess import Popen, PIPE

import sys

from conf import base_api_link, user, passwd
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


def send_file_results(file, results):
    log('Sending results for file {}.'.format(file))
    file_comments = SendResultsToPullRequestFiles(base_api_link=base_api_link,
                                                  checked_file=file,
                                                  username=user,
                                                  passwd=passwd)
    file_comments.send_static_check_results(results)
    log('Sending results finished. Output: {}'.format(file_comments))


def static_check_java(file_to_check, cmd, report_flag, check_type):
    code, result = execute_linux_command(cmd)
    if code != 0:
        count = 'Error while executing static check: {}'.format(result)
    else:
        i = 0
        log('Trying to count errors in file {0}_{1}.xml'.format(
                file_to_check, check_type
        )
        )
        with open('{0}_{1}.xml'.format(file_to_check, check_type), 'r') as f:
            for line in f:
                if report_flag in line: i += 1
        count = i
    return count


def static_check_swift(file_to_check, cmd, result_file):
    code, result = execute_linux_command(cmd)

    if code != 0:
        count = (-1, 'Error while executing static check: {}'.format(result))
    else:
        log('Trying to count errors in file {}'.format(result_file))
        with open(result_file, 'r') as f:
            result_json = f.read().replace('\n', '')
        report = json.loads(result_json)
        count = report['summary']
        log('Tailor summary: {0}'.format(count))

    return count


def commit_files_handler(commit_id, required_extension):
    # Here we will get list of files, that have been changed in this
    # commit, if command succeed.
    cmd = 'git diff-tree --no-commit-id --name-only -r {}'.format(commit_id)
    code, out = execute_linux_command(cmd)
    log('List of files changed in commit received: {}'.format(out))
    # Generate list of files
    files = [file for file in out.split('\n')]
    for file in files:
        # If file is not required type, then go to next file.
        if not file or required_extension not in file:
            continue
        log('Checking file {}'.format(file))
        # Here is some hardcode, but it is really necessary,
        # trust me, I'm a drummer!
        if required_extension == '.java':
            # PMD check:
            pmd_rules = os.environ.get("PMD_RULES", "java-codesize,java-empty,"
                                                    "java-imports,java-strings"
                                       )
            cmd = (
                'pmd/bin/run.sh pmd -l java --failOnViolation false -f xml'
                ' -r {0}_pmd.xml -d {0} -R {1}'.format(file, pmd_rules)
            )
            violations = '</violation>'
            pmd_count = static_check_java(file, cmd, violations, 'pmd')
            log('PMD count for file {0}: {1}'.format(file, pmd_count))
            # Checkstyle_check
            checkstyle_rules = os.environ.get("CHECKSTYLE_RULES",
                                              './google_checks.xml')
            cmd = (
                'java -jar checkstyle.jar -f xml -o {0}_checkstyle.xml '
                '-c {1} {0}'.format(file, checkstyle_rules)
            )
            violations = '<error'
            checkstyle_count = static_check_java(file, cmd, violations,
                                            'checkstyle')
            log('Checkstyle count for file {0}: {1}'.format(file,
                                                            checkstyle_count))
            # Aggregating results:
            result = {
                'PMD errors: ': pmd_count,
                'Checkstyle errors: ': checkstyle_count
            }

            send_file_results(file, result)
        elif required_extension == '.swift':
            log('Checking file {}'.format(file))
            tailor_file = "tailor_{0}.json".format(file.replace('/', '_'))
            cmd = '/usr/local/bin/tailor -f json {0} > {1}'.format(file,
                                                                   tailor_file)

            tailor_count = static_check_swift(file, cmd, tailor_file)

            if type(tailor_count) == tuple:
                log('Error while tailoring file {0}: {1}'.format(file,
                                                                 tailor_count[1]))
            else:
                log('Tailor results for file {0}: {1}'.format(file,
                                                              tailor_count))
                tailor_message = (
                    'violations: {0}, errors: {1}, warnings: {2}, skipped: {3}'
                    .format(tailor_count['violations'], tailor_count['errors'],
                            tailor_count['warnings'], tailor_count['skipped'])
                )
                result = {'Tailor Swift reports:': tailor_message}
                send_file_results(file, tailor_count)


def main():
    pr = PullRequestCommits(base_api_link=base_api_link, username=user,
                            passwd=passwd)
    commit_list = pr.get_commits()
    log('List of commits for pull request received: {}'.format(commit_list))

    for commit_id in commit_list:
        log('Processing commit ID {}'.format(commit_id))
        commit_files_handler(commit_id, sys.argv[1])


if __name__ == '__main__':
    main()
