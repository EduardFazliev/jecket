import argparse
import logging.config
import yaml

import set_conf
import set_status
import static_check
import send_comment



def invoke_set_status(args):
    if not (args.successful, args.failed, args.in_progress):
        print("No status was provided.")
    elif args.successful:
        set_status.main("SUCCESSFUL")
    elif args.failed:
        set_status.main("FAILED")
    elif args.in_progress:
        set_status.main("INPROGRESS")
    else:
        print 'No status argument was provided.'


def invoke_static_check(args):
    if args.all:
        static_check.main(func='all', ext=args.extension)
    elif args.pull_request:
        static_check.main(func='pr', ext=args.extension)
    elif args.file is not None:
        static_check.main(func='file', ext=args.extension, filename=args.file)
    else:
        print 'No source was provided for static check.'


def invoke_send_pr_comment(args):
    send_comment.main(args.comment)


def invoke_set_conf(args):

    if args.base_link is None and args.username is None and args.password is None:
        print 'No data given.'
    else:
        set_conf.main(args)

def parse_args():
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
