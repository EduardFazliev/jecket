#!/usr/bin/env python
import json
import os

import jbi_exceptions
from jbi_logger import log
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
        log('Sending build status for commit {}.'.format(commit_hash))
        payload = {
            "state": state,
            "key": key,
            "url": url
        }
        content, status = self.send_post_request(url, payload)
        log('Sending finished. Result: status - {0}, content - {1}.'.format(
                status, content
        )
        )
        return content, status


class PullRequestCommits(SendResultsToPullRequestFiles):
    def __init__(self, base_api_link, username, passwd):
        super(PullRequestCommits, self).__init__(
            base_api_link, '', username, passwd
        )

    def generate_url(self):
        """This method is generate correct url for bitbucket api.

        Returns:
            url (str): api url for adding comments.
        """
        log('Generating URL for using REST API...')
        slug = os.environ.get("SLUGNAME", 'DOCM')
        project_name = os.environ.get("PROJECT_NAME", 'infotech-ansible')
        pull_request_id = os.environ.get("PRI", '9')

        url = self.base_api_link
        url = url.replace('{SLUG}', slug)
        url = url.replace('{PROJECT}', project_name)
        url = url.replace('{PRI}', pull_request_id)
        if url[-1] != '/':
            url += '/'
        url = '{0}commits'.format(url)
        log('URL generated: {}'.format(url))
        return url

    def get_commits(self):
        url = self.generate_url()
        payload = {"withcounts": "false"}
        content, code = self.send_get_request(url, payload)
        if code == 200:
            commits = json.loads(content)
            result = [commit['id'] for commit in commits['values']]
        else:
            raise jbi_exceptions.IncorrectJsonException(status=code, url=url,
                                                        json=content)
        return result
