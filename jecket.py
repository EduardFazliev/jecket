import argparse
import logging.config
import yaml

import set_conf
import send_comment
import set_status
import static_check


def invoke_set_status(args):
    """The function invokes `set_status` module with the following argument
    which sets the status of pull-request to one of three: In progress,
    Successful or Failed.

    Args:
        args: type of status. Expected values are `in_progress`, `successful`,
         or `failed`.

    Returns:
        None
    """
    if not any([args.successful, args.failed, args.in_progress]):
        print("No status was provided.")
    elif args.successful:
        set_status.main("SUCCESSFUL")
    elif args.failed:
        set_status.main("FAILED")
    elif args.in_progress:
        set_status.main("INPROGRESS")


def invoke_static_check(args):
    """The function invokes `static_check` module with the following argument
    which sends static check result to files, that was changed in pull request.

    Args:
        args: Type of check to perform. Expected values are `all`,
         `pull_request` or `file`.

    Returns:
        None
    """
    if args.all:
        static_check.main(func='all', ext=args.extension)
    elif args.pull_request:
        static_check.main(func='pr', ext=args.extension)
    elif args.file is not None:
        static_check.main(func='file', ext=args.extension, filename=args.file)
    else:
        print 'No source was provided for static check.'


def invoke_send_pr_comment(args):
    """The function invokes `send_comment` module with the following argument
    which sends comments to a pull-request.

    Args:
        args: Text comment.

    Returns:
        None

    """
    send_comment.main(args.comment)


def invoke_set_conf(args):
    """The function invokes `set_conf` module with the following arguments

    Args:
        args: Configuration settings. Expected values are `base_link`,
        `username` and `password`.

    Returns:
        None

    """
    if None in (args.base_link, args.username, args.password):
        print 'Missing required arguments.'
    else:
        set_conf.main(args)


def parse_args():
    """ The function creates a command-line interface with appropriate
    positional and optional arguments to interact with the program.

    Returns: None

    """
    parser = argparse.ArgumentParser()
    # parser.add_argument("command", type=str, help="Command to execute, for example: set-status, send-comment")
    subparsers = parser.add_subparsers(help="sub-command help")

    # Generate conf file for jecket.
    parser_set_conf = subparsers.add_parser("set-conf", help="Generate conf file for jecket.")
    parser_set_conf.add_argument("-l", "--base-link", type=str, help="Base link to your BitBucket server. "
                                                                     "For example: http://somecompany.bitbucket.com.")
    parser_set_conf.add_argument("-u", "--username", type=str, help="Username for basic authorization"
                                                                    "on bitbucket server.")
    parser_set_conf.add_argument("-p", "--password", type=str, help="Password for basic authorization "
                                                                    "on bitbucket server.")
    parser_set_conf.set_defaults(func=invoke_set_conf)

    # Send static check result to files, that was changed in pull request.
    parser_static_check = subparsers.add_parser("static-check",
                                                help="Sends static check results for specific file types.")
    parser_static_check.add_argument("-e", "--extension", type=str, help="File extension with dot.")
    static_check_group = parser_static_check.add_mutually_exclusive_group()
    # Group for choosing one of checking option: single file, files,
    # that was changed in commits in pull-request, or full project.
    static_check_group.add_argument("-f", "--file", type=str, help="Full or relative path to file, "
                                                                   "that will be checked.")
    static_check_group.add_argument("-p", "--pull-request", action="store_true", help="Check all files, that "
                                                                                      "was changed in pull-request.")
    static_check_group.add_argument("-a", "--all", action="store_true", help="Check all project.")
    parser_static_check.set_defaults(func=invoke_static_check)

    # Set status of pull request.
    parser_set_status = subparsers.add_parser("set-status", help="Set status of pull-request to one of three: "
                                                                 "in progress, successful or failed")
    status_group = parser_set_status.add_mutually_exclusive_group()
    status_group.add_argument("-s", "--successful", action="store_true", help="Set status to SUCCESSFUL.")
    status_group.add_argument("-f", "--failed", action="store_true", help="Set status to FAILED.")
    status_group.add_argument("-p", "--in-progress", action="store_true", help="Set status to IN PROGRESS.")
    parser_set_status.set_defaults(func=invoke_set_status)

    parser_send_pr_comment = subparsers.add_parser('send-pr-comment', help="Send comments to pull-request.")
    parser_send_pr_comment.add_argument("-c", "--comment", type=str, help="Comment text.")
    parser_send_pr_comment.set_defaults(func=invoke_send_pr_comment)

    args = parser.parse_args()
    args.func(args)


def main():
    logger = logging.getLogger(__name__)
    logger.info('Jecket welcomes you!')
    parse_args()


if __name__ == "__main__":
    with open("logger.yaml", "r") as log_conf:
        logging.config.dictConfig(yaml.load(log_conf))
    main()
