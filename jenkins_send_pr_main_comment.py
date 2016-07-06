import sys

from conf import base_api_link, user, passwd
from pull_request_main_comments_section import SendResultsToPullRequest


def main():
    pr = SendResultsToPullRequest(base_api_link=base_api_link, username=user,
                                  passwd=passwd)
    comment = sys.argv[1]
    pr.send_comment()


if __name__ == '__main__':
    main()
