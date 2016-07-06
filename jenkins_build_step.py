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
    try:
        proc = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
        out, err = proc.communicate()
        code = proc.returncode
    except Exception as e:
        log('Error occurred while executing command {}: {}'.format(cmd, e))
        result = (-1, e)
    else:
        log('Command code"{0}, result"{1}, error:{2}'.format(code, out, err))
        if code != 0:
            result = (code, err)
        elif code == 0:
            result = (code, out)
    finally:
        return result


def send_file_results(target_file, results):
    """Function sends dictionary with results to
        send_static_check_results method.

    Args:
        target_file (str): relative path to file in repository,
            that will be commented.
        results (dict of error_title:error_value):
            {
                error_title (str): Type of error.
                    Example: pmd, checkstyle, violation, warning.
                error_value (int): Number of errors if this type.
            }
    """
    log('Sending results for file {}.'.format(target_file))
    file_comments = SendResultsToPullRequestFiles(base_api_link=base_api_link,
                                                  checked_file=target_file,
                                                  username=user,
                                                  passwd=passwd)
    result = file_comments.send_static_check_results(results)
    log(
        'Sending results finished. Output: code: {0}, '
        'content: {1}'.format(result[0], result[1])
    )


def static_check_java(file_to_check, cmd, report_flag, check_type):
    """Function executes command, that generate report file (cmd)
        and counts lines with that contains special line (report_flag).

    Args:
        file_to_check (str): Relative path to report file.
        cmd (str): Linux command, that needs to be executed.
        report_flag (str): String, that indicates violation.
        check_type (str): Type of static check.
    """
    code, result = execute_linux_command(cmd)
    if code != 0:
        count = (-1, 'Error while executing static check: {}'.format(result))
    else:
        i = 0
        log('Trying to count errors in file {0}_{1}.xml'.format(file_to_check,
                                                                check_type))
        with open('{0}_{1}.xml'.format(file_to_check, check_type), 'r') as f:
            for line in f:
                if report_flag in line:
                    i += 1
        count = i
    return count


def static_check_swift(cmd, result_file):
    """Function is loads file with Tailor report in JSON format
    to string and returns summary section.

     Args:
         cmd (str): Linux command to invoke. Basically it executes
            Tailor with '-f json' argument.
         result_file (str): Relative path to file with Tailor output.
            File must be created by invoking 'cmd' command and must
            contain Tailor check results in JSON format.

    Returns:
        If return code ('code') equal 200 or 204:
        count (dict of title: value):
            title (str): Type of violation.
            value (str): Number of violations of this type in file.
        If return code ('code') not equal 200 or 204 or
            exception occurred:
        count (tuple of (status, error)):
            status (int): Error code.
            error (str): Error description.
    """
    code, result = execute_linux_command(cmd)

    if code != 0:
        count = (-1, 'Error while executing static check: {}'.format(result))
    else:
        log('Trying to count errors in file {}'.format(result_file))
        try:
            with open(result_file, 'r') as f:
                result_json = f.read().replace('\n', '')
        except IOError as e:
            log('Error while processing file {0}: {1}'.format(result_file, e))
            count = (-1, e)
        else:
            try:
                report = json.loads(result_json)
            except ValueError as e:
                log('JSON loads operation is ended with error: {0}'.format(e))
                count = (-1, e)
            else:
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

            tailor_count = static_check_swift(cmd, tailor_file)

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
                send_file_results(file, result)


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
