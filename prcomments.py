#!/usr/bin/env python
import json
import os

import jecket_exceptions
from jbi_logger import log
from pull_request_file_comments import PRFile


class PRState(PRFile):
    rest_api_link = '/rest/build-status/1.0/commits/'

    def __init__(self, base_api_link, username, passwd):
        super(PRState, self).__init__(base_api_link, '', username, passwd)

    def send_comment(self, comment):
        url = self.generate_url()
        payload = {"text": comment}
        return self.send_post_request(url, payload)

    def send_build_status(self, state, key, url_to_build):
        commit_hash = os.environ.get("GIT_COMMIT", "TEST_HASH")
        url = self.base_api_link + PRState.rest_api_link + commit_hash
        log('Sending build status for commit {}.'.format(commit_hash))
        payload = {
            "state": state,
            "key": key,
            "url": url_to_build
        }
        code, content = self.send_post_request(url, payload)
        log('Sending finished. Result: status - {0}, content - {1}.'.format(code, content))
        return (code, content)


class PRCommits(PRFile):
    def __init__(self, base_api_link, username, passwd):
        super(PRCommits, self).__init__(base_api_link, '', username, passwd)

    def generate_url(self):
        """This method is generate correct url for bitbucket api.

        Returns:
            url (str): api url for adding comments.
        """
        if self.slug is None:
            log("Slug is not provided to class, trying to get it from environment variable.")
            slug = os.environ.get("SLUG", "TEST_KEY")
        else:
            slug = self.slug

        if self.project_name is None:
            log("Project name is not provided to class, trying to get it from environment variable.")
            project_name = os.environ.get("PROJECT", "TEST_REPO")
        else:
            project_name = self.project_name

        if self.pull_request_id is None:
            log("Pull request ID is not provided to class, trying to get it from environment variable.")
            pull_request_id = os.environ.get("PR_ID", "TEST_ID")
        else:
            pull_request_id = self.pull_request_id

        url = self.base_api_link + self.rest_api_link
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
        code, message = self.send_get_request(url, payload)
        if code in [200, 204]:
            commits = json.loads(message)
            result = [commit['id'] for commit in commits['values']]
        else:
            raise jecket_exceptions.IncorrectJsonException(status=code, url=url,
                                                           json=message)
        return result
