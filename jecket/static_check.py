import json
import logging
import os
from subprocess import Popen, PIPE

import jecket


logger = logging.getLogger(__name__)


def execute_linux_command(cmd):
    """The function creates a subprocess to execute linux command, then
    returns the execution code and the result.

    Args:
        cmd: shell command
    """
    result = (-1, 'Unknown Error.')
    logger.debug('Executing command {}'.format(cmd))
    try:
        proc = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
        out, err = proc.communicate()
        code = proc.returncode
    except Exception as e:
        logger.exception('Error occurred while executing command {}.'.format(cmd))
        result = (-1, e)
    else:
        logger.debug('Command code"{0}, result"{1}, error:{2}'.format(code, out, err))
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
    logger.debug('Sending results for file {}.'.format(target_file))
    file_comments = jecket.PRFile(checked_file=target_file)
    code, message = file_comments.send_static_check_results(results)
    logger.info("Sending results finished.")
    logger.debug(
        "Sending results finished. Output: code: {0}, content: {1}".format(
            code, message))
    return code, message


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
        logger.debug(
            'Trying to count errors in file {0}_{1}.xml'.format(file_to_check,
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
        logger.debug('Trying to count errors in file {}'.format(result_file))
        try:
            with open(result_file, 'r') as f:
                result_json = f.read().replace('\n', '')
        except IOError as e:
            logger.debug(
                'Error while processing file {0}: {1}'.format(result_file, e))
            count = (-1, e)
        else:
            try:
                report = json.loads(result_json)
            except ValueError as e:
                logger.debug(
                    'JSON loads operation is ended with error: {0}'.format(e))
                count = (-1, e)
            else:
                count = report['summary']
                logger.debug('Tailor summary: {0}'.format(count))

    return count


def count_lines(filename):
    i = -1
    with open(filename) as f:
        for i, _ in enumerate(f):
            pass
        logger.debug('File line enumerate counter result: {}'.format(i))
    return i + 1


def java_file_handler(changed_file):
    """The function performs PMD and Checkstyle checks for a .java file,
    and returns the results.

    Args:
        changed_file: .java file
    """

    # PMD check: #####

    pmd_rules = os.environ.get("PMD_RULES",
                               "java-codesize,java-empty,java-imports,java-strings")
    cmd = (
        'pmd/bin/run.sh pmd -l java --failOnViolation false -f xml -r {0}_pmd.xml -d {0} -R {1}'
        .format(changed_file, pmd_rules)
    )

    # XML tag for violations
    violations = '</violation>'
    pmd_count = static_check_java(changed_file, cmd, violations, 'pmd')
    logger.debug('PMD count for file {0}: {1}'.format(changed_file, pmd_count))

    # Checkstyle_check #####
    checkstyle_rules = os.environ.get("CHECKSTYLE_RULES",
                                      './google_checks.xml')
    cmd = 'java -jar checkstyle.jar -f xml -o {0}_checkstyle.xml -c {1} {0}'.format(
        changed_file, checkstyle_rules)

    violations = '<error'
    checkstyle_count = static_check_java(changed_file, cmd, violations,
                                         'checkstyle')
    logger.debug('Checkstyle count for file {0}: {1}'.format(changed_file,
                                                             checkstyle_count))
    # Aggregating results:
    result = {
        'PMD errors: ': pmd_count,
        'Checkstyle errors: ': checkstyle_count
    }

    code, message = send_file_results(changed_file, result)
    return code, message


def swift_file_handler(changed_file):
    """The function performs Tailor check for a .swift file and returns
    the report.

    Args:
        changed_file: .swift file
    """
    tailor_file = "tailor_{0}.json".format(changed_file.replace('/', '_'))
    cmd = '/usr/local/bin/tailor -f json {0}  > {1}'.format(changed_file,
                                                            tailor_file)

    tailor_count = static_check_swift(cmd, tailor_file)

    if type(tailor_count) == tuple:
        logger.debug('Error while tailoring file {0}: {1}'.format(changed_file,
                                                                  tailor_count[
                                                                      1]))
        code, message = (-1, tailor_count[1])
    else:
        logger.debug('Tailor results for file {0}: {1}'.format(changed_file,
                                                               tailor_count))
        tailor_message = (
                'violations: {0}, errors: {1}, warnings: {2}, skipped: {3}'
                .format(tailor_count['violations'], tailor_count['errors'],
                        tailor_count['warnings'],
                        tailor_count['skipped'])
        )
        result = {'Tailor Swift reports:': tailor_message}
        code, message = send_file_results(changed_file, result)
    return code, message


def go_file_handler(changed_file):
    """The function performs Golint check for a .go file and returns
    the report.

    Args:
        changed_file: .go file
    """
    report_file = '{0}.golint'.format(changed_file.replace('/', '_'))
    cmd = 'golint -min_confidence 0.1 {0} > {1} 2>&1'.format(changed_file,
                                                             report_file)
    execute_linux_command(cmd)
    golint_count = count_lines(report_file)
    golint_message = 'Violations: {0}'.format(golint_count)
    logger.debug('GoLint message: {0}'.format(golint_message))
    result = {'GoLint reports:': golint_message}
    code, message = send_file_results(changed_file, result)
    return code, message


def file_handler(checked_file, required_extension):
    """The function defines file extension and executes appropriate check.

    Args:
        checked_file: inspected file
        required_extension: file extension
    """
    # If file is not required type, then go to next file.
    result = (-42, "Unknown.")
    if not checked_file or required_extension not in checked_file:
        result = (0, 'Not checked.')
    else:
        logger.debug('Checking file {}'.format(checked_file))
        # Here is some hardcode, but it is really necessary,
        # trust me, I'm a drummer!
        if required_extension == '.java':
            result = java_file_handler(checked_file)
        elif required_extension == '.swift':
            result = swift_file_handler(checked_file)
        elif required_extension == '.go':
            result = go_file_handler(checked_file)
        else:
            result = (0, 'Not checked. Unsupported extension.')
    return result


def check_single_file(ext, filename):
    """The function performs a single file check.

    Args:
        ext: file extension
        filename: file name
    """
    file_handler(filename, ext)


def check_pr(ext):
    """The function performs a check for changed files from a pull request
    for a given extension.

    Args:
        ext: file extension
    """
    logger.info("Start checking pull-request...")
    pr = jecket.PRCommits()
    # Get list of commits SHA, that are in pull-request.
    commit_list = pr.get_commits()
    logger.debug(
        'List of commits for pull request received: {}'.format(commit_list))

    for commit_id in commit_list:
        logger.info('Processing commit ID {}'.format(commit_id))

        # Here we will get list of files, that have been changed in this
        # commit, if command succeed.
        cmd = 'git diff-tree --no-commit-id --name-only -r {}'.format(commit_id)
        code, out = execute_linux_command(cmd)
        logger.debug('List of files changed in commit received: {}'.format(out))
        # Generate list of files
        changed_files = [changed_file for changed_file in out.split('\n')]

        for changed_file in changed_files:
            file_handler(changed_file, ext)


def check_all_project(ext):
    print "Check all project in a pull-request? Why would you do that?"


def main(func, ext, filename=''):
    logging.getLogger(__name__)
    if func == 'all':
        check_all_project(ext)
    elif func == 'pr':
        check_pr(ext)
    elif func == 'file':
        check_single_file(ext, filename)


if __name__ == '__main__':
    main()
