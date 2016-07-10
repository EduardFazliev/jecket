import argparse
import logging.config
import yaml

import set_status


def invoke_set_status(args):
    if not (args.successful, args.failed, args.in_progress):
        print("No status was provided.")
    elif args.successful:
        set_status.main("SUCCESSFUL")
    elif args.failed:
        set_status.main("FAILED")
    elif args.in_progress:
        set_status.main("INPROGRESS")


def parse_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument("command", type=str, help="Command to execute, for example: set-status, send-comment")
    subparsers = parser.add_subparsers(help="sub-command help")

    # Generate conf file for jecket.
    parser_set_conf = subparsers.add_parser("set-conf", help="Generate conf file for jecket.")
    parser_set_conf.add_argument("-l", "--base-link", type=str, help="Base link to your BitBucker server. "
                                                                     "For example: http://somecompany.bitbucket.com.")
    parser_set_conf.add_argument("-u", "--username", type=str, help="Username for basic authorization"
                                                                    "on bitbucket server.")
    parser_set_conf.add_argument("-p", "--password", type=str, help="Password for basic authorization "
                                                                    "on bitbucket server.")
    # Send static check result to files, that was changed in pull request.
    parser_static_check = subparsers.add_parser("static_check",
                                                help="Sends static check results for specific file types. ")
    parser_static_check.add_argument("-f", "--file-extension", type=str, help="File extension with dot.")

    # Set status of pull request.
    parser_set_status = subparsers.add_parser("set-status", help="Set status of pull-request to one of three: "
                                                                 "in progress, successful or failed")
    status_group = parser_set_status.add_mutually_exclusive_group()
    status_group.add_argument("-s", "--successful", action="store_true", help="Set status to SUCCESFUL.")
    status_group.add_argument("-f", "--failed", action="store_true", help="Set status to FAILED.")
    status_group.add_argument("-p", "--in-progress", action="store_true", help="Set status to IN PROGRESS.")
    parser_set_status.set_defaults(func=invoke_set_status)

    args=parser.parse_args()
    args.func(args)

def main():
    logger = logging.getLogger(__name__)
    logger.info('Jecket welcomes you!')
    parse_args()


if __name__ == "__main__":
    with open("logger.yaml", "r") as log_conf:
        logging.config.dictConfig(yaml.load(log_conf))
    main()