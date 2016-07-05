import os
import sys

from conf import base_api_link, base_build_status_link, user, passwd
from jbi_logger import log
from pull_request_main_comments_section import SendResultsToPullRequest


def main():
    pr = SendResultsToPullRequest(base_api_link=base_api_link, username=user,
                                  passwd=passwd,
                                  base_build_status_link=base_build_status_link
                                  )

    status = sys.argv[1]
    key = os.environ.get("JOB_NAME", 'Custom BUILD_TAG')
    url = os.environ.get("BUILD_URL", 'http://custombuildurl.com')
    log('Pull Request status:{0}, key:{1}, url:{2}'.format(status, key, url))
    pr.send_build_status(status, key, url)


if __name__ == '__main__':
    main()
