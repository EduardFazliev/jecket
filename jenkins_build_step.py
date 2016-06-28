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


def send_file_results(file, pmd, checkstyle):
    log('Sending results for file {}.'.format(file))
    file_comments = SendResultsToPullRequestFiles(
        base_api_link=base_api_link,
        checked_file=file,
        username=user,
        passwd=passwd
    )
    file_comments.send_static_check_results(pmd, checkstyle)
    log('Sending results finished. Output: {}'.format(file_comments))


def static_check(file_to_check, cmd, report_flag, check_type):
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


def commit_files_handler(commit_id):
    cmd = 'git diff-tree --no-commit-id --name-only -r {}'.format(commit_id)
    code, out = execute_linux_command(cmd)
    log('List of files changed in commit received: {}'.format(out))
    files = [file for file in out.split('\n')]
    for file in files:
        if not file or '.java' not in file:
            continue
        log('Checking file {}'.format(file))
        pmd_rules = os.environ.get("PMD_RULES", "java-codesize,java-empty,java-imports,java-strings")
        cmd = 'pmd/bin/run.sh pmd -l java --failOnViolation false -f xml -r {0}_pmd.xml -d {0} -R {1}'.format(file, pmd_rules)
        violations = '</violation>'
        pmd_count = static_check(file, cmd, violations, 'pmd')
        log('PMD count for file {0}: {1}'.format(file, pmd_count))

        checkstyle_rules = os.environ.get("CHECKSTYLE_RULES", './google_checks.xml')
        cmd = 'java -jar checkstyle.jar -f xml -o {0}_checkstyle.xml -c {1} {0}'.format(file, checkstyle_rules)
        violations = '<error'
        checkstyle_count = static_check(file, cmd, violations, 'checkstyle')
        log('Checkstyle count for file {0}: {1}'.format(file, checkstyle_count))

        send_file_results(file, pmd_count, checkstyle_count)


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
