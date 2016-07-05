#!/usr/bin/env python
import json
import os

import jbi_exceptions
from jbi_logger import log
from pull_request_file_comments import SendResultsToPullRequestFiles


class SendResultsToPullRequest(SendResultsToPullRequestFiles):
    rest_api_link = '/rest/build-status/1.0/commits/'

    def __init__(self, base_api_link, username, passwd):
        super(SendResultsToPullRequest, self).__init__(base_api_link, '',
                                                       username, passwd)

    def send_comment(self, comment):
        url = self.generate_url()
        payload = {"text": comment}
        content, code = self.send_post_request(url, payload)
        return content, code

    def send_build_status(self, state, key, url_to_build):
        commit_hash = os.environ.get("GIT_COMMIT")
        url = (self.base_api_link + SendResultsToPullRequest.rest_api_link +
               commit_hash)
        log('Sending build status for commit {}.'.format(commit_hash))
        payload = {
            "state": state,
            "key": key,
            "url": url_to_build
        }
        content, status = self.send_post_request(url, payload)
        log('Sending finished. Result: status - {0}, '
            'content - {1}.'.format(status, content))
        return content, status


class PullRequestCommits(SendResultsToPullRequestFiles):
    def __init__(self, base_api_link, username, passwd):
        super(PullRequestCommits, self).__init__(base_api_link, '', username,
                                                 passwd)

    def generate_url(self):
        """This method is generate correct url for bitbucket api.

        Returns:
            url (str): api url for adding comments.
        """
        log('Generating URL for using REST API...')
        slug = os.environ.get("SLUG", 'DOCM')
        project_name = os.environ.get("PROJECT", 'infotech-ansible')
        pull_request_id = os.environ.get("PR_ID", '9')

        url = self.base_api_link + SendResultsToPullRequestFiles.rest_api_link
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
