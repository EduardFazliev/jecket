import sys

from conf import base_api_link, user, passwd
from jbi_logger import log
from pull_request_main_comments_section import SendResultsToPullRequest


def main():
    pr = SendResultsToPullRequest(base_api_link=base_api_link, username=user, passwd=passwd)
    comment = sys.argv[1]
    log("Sending comment {} to pull request.".format(comment))
    code, content = pr.send_comment(comment=comment)
    log("Comment to pull request sent. Code: {0}, content: {1}".format(code, content))


if __name__ == '__main__':
    main()
