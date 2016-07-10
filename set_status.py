import logging
import os
try:
    from conf import base_api_link, user, passwd
except Exception as e:
    import jecket_exceptions
    raise  jecket_exceptions.IncorrectConfigFileException(e)
from pull_request_main_comments_section import SendResultsToPullRequest


def main(status):
    logging.getLogger(__name__)
    pr = SendResultsToPullRequest(base_api_link=base_api_link, username=user, passwd=passwd)
    key = os.environ.get("JOB_NAME", "Custom BUILD_TAG")
    url = os.environ.get("BUILD_URL", "http://custombuildurl.com")
    logging.debug('Pull Request status:{0}, key:{1}, url:{2}'.format(status, key, url))
    logging.info("Trying to set pull request status...")
    code, message = pr.send_build_status(status, key, url)
    logging.debug("Finished. Code: {0}, message: {1}".format(code, message))
    logging.info("Returned status: {}".format(code))


if __name__ == '__main__':
    main()
