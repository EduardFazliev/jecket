import logging

from conf import base_api_link, user, passwd
from prcomments import PRState


def main(comment):
    logger = logging.getLogger(__name__)
    pr = PRState(base_api_link=base_api_link, username=user, passwd=passwd)
    logger.info("Sending comment {} to pull request.".format(comment))
    code, content = pr.send_comment(comment=comment)
    logger.info(
        "Comment to pull request sent. Code: {0}, content: {1}".format(code,
                                                                       content))


if __name__ == '__main__':
    main()
