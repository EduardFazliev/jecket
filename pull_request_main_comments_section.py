#!/usr/bin/env python
import json
import os

from pull_request_file_comments import SendResultsToPullRequestFiles


class SendResultsToPullRequest(SendResultsToPullRequestFiles):
    def __init__(self, base_api_link, username, passwd, base_build_status_link):
        super(SendResultsToPullRequest, self).__init__(
            base_api_link, '', username, passwd
        )
        self.base_build_status_link = base_build_status_link

    def send_comment(self, comment):
        url = self.generate_url()
        payload = {"text": comment}
        content, code = self.send_post_request(url, payload)
        return content, code

    def send_build_status(self, state, key, url):
        commit_hash = os.environ.get("GIT_COMMIT", "6f313785de6ea011b4107f18d1adbf427f28e058")
        url = self.base_build_status_link + commit_hash
        print url
        payload = {
            "state": state,
            "key": key,
            "url": url
        }
        content, status = self.send_post_request(url, payload)
        return content, status
