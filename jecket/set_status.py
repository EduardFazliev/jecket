import logging
import os

import jecket


logger = logging.getLogger(__name__)


def main(status):
    pr = jecket.PRState()
    key = os.environ.get("JOB_NAME", "Custom BUILD_TAG")
    url = os.environ.get("BUILD_URL", "http://custombuildurl.com")
    logger.debug('Pull Request status:{0}, key:{1}, url:{2}'.format(status, key, url))
    logger.info("Trying to set pull request status...")
    code, message = pr.send_build_status(status, key, url)
    logger.debug("Finished. Code: {0}, message: {1}".format(code, message))
    logger.info("Returned status: {}".format(code))


if __name__ == '__main__':
    main()
