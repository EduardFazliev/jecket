import os
import sys

from conf import base_api_link, user, passwd
from jbi_logger import log
from pull_request_main_comments_section import SendResultsToPullRequest


def main():
    pr = SendResultsToPullRequest(base_api_link=base_api_link, username=user, passwd=passwd)
    status = sys.argv[1]
    key = os.environ.get("JOB_NAME", "Custom BUILD_TAG")
    url = os.environ.get("BUILD_URL", "http://custombuildurl.com")
    log('Pull Request status:{0}, key:{1}, url:{2}'.format(status, key, url))
    log("Trying to set pull request status...")
    code, message = pr.send_build_status(status, key, url)
    log("Finished. Code: {0}, message: {1}".format(code, message))


if __name__ == '__main__':
    main()
