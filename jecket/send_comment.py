import logging

import jecket


logger = logging.getLogger(__name__)


def main(comment):
    pr = jecket.PRState()
    logger.info('Sending comment {} to pull request.'.format(comment))
    code, content = pr.send_comment(comment=comment)
    logger.info('Comment to pull request sent. Code: {0}, content: {1}'.format(code, content))


if __name__ == '__main__':
    main()
