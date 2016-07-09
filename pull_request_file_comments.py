#!/usr/bin/env python

import json
import os
import requests
from requests.auth import HTTPBasicAuth

from jbi_logger import log


# noinspection PyShadowingBuiltins
class SendResultsToPullRequestFiles(object):
    """
    This class sends static checks results to pull request files.
    """
    checks_author = 'jenkins'
    rest_api_link = '/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/'

    def __init__(self, base_api_link, checked_file, username, passwd):
        """Args:
            base_api_link (str): link to bitbucket's api service.
            checked_file (str): path to file, that is going
                to be checked with static checks.
            username (str): login for basic auth.
            passwd (str): password for basic auth.
        """
        self.username = username
        self.passwd = passwd
        self.base_api_link = base_api_link
        self.checked_file = checked_file

    def generate_url(self):
        """This method is generate correct url for bitbucket api.

        Returns:
            url (str): API URL for adding comments.
        """
        slug = os.environ.get("SLUG", "TEST_KEY")
        project_name = os.environ.get("PROJECT", "TEST_REPO")
        pull_request_id = os.environ.get("PR_ID", "TEST_ID")

        url = self.base_api_link + SendResultsToPullRequestFiles.rest_api_link
        url = url.replace('{SLUG}', slug)
        url = url.replace('{PROJECT}', project_name)
        url = url.replace('{PRI}', pull_request_id)
        if url[-1] != '/':
            url += '/'
        url = '{0}comments'.format(url)
        return url

    def send_static_check_results(self, results):
        """Method sends static check results (PMD and checkstyle
        for now) as a comment for specific file in commit.

        Args:
            results (dict of title: value):
                {
                    title (str): value (str)
                }
                title: Violation description.
                value: Number of violations.

        Returns:
            content (str): Respond's payload.
            code (int): Response's code.
        """
        build_link = os.environ.get("BUILD_URL", "http://jenkins.test")
        text = ''
        for key in results.iterkeys():
            text += "{0} {1}".format(key, results[key])
        text += " You can find details via link {}".format(build_link)

        # Get result into temp variable, and check.
        temp = self.check_comments_from_specific_author(SendResultsToPullRequestFiles.checks_author)

        # if result is None, then we need to Post comment,
        # if result is Not none, then we need to PUT comment.
        if temp is None:
            url = self.generate_url()
            payload = {"text": text, "anchor": {"path": self.checked_file}}
            content, code = self.send_post_request(url, payload)
        else:
            # And to PUT we need to pass additional parameters:
            # id of existing comment and it's version.
            id, version = temp
            url = self.generate_url()
            self.base_api_link = '{0}/{1}'.format(url, id)
            payload = {
                "version": version,
                "text": text,
                "anchor": {
                    "path": self.checked_file
                }
            }
            content, code = self.send_put_request(self.base_api_link, payload)
        return content, code

    def check_comments_from_specific_author(self, author):
        """Method searches for comments from specific author.

        Args:
            author (str): Username of author.

        Returns:
            comment_id (str): 'Error' if error occurred while searching
            for comments from specific author or comment ID of first
            found comment or None if nothing is found and there is no
            errors.
        """
        log('Searching comments from {}'.format(author))
        result = None
        comments = self.get_all_comments_for_file()
        if comments == 'Error':
            result = 'Error'
        else:
            for comment in comments:
                if comment["author"]["name"] == author:
                    comment_id = (comment["id"], comment["version"])
                    result = comment_id
                    log('Found comment for file {0} by author {1}'.format(self.checked_file, author))
                    break
        return result

    def get_all_comments_for_file(self):
        """Method for collectiong all comments for specific file.

        Returns:
            result (dict of str): dictionary with comments.
        """
        payload = {'path': self.checked_file}
        url = self.generate_url()
        content, code = self.send_get_request(url, payload)
        response = json.loads(content)

        if code in [200, 204]:
            result = response["values"]
        else:
            result = 'Error'
        return result

    def send_post_request(self, url, payload):
        """Sends post request with spec header.

        Args:
            url (str): API URL to send comment.
            payload (dict): json to send.

        Returns:
            result.content (dict): Response content in json format.
            result.status_code (str): Response code.
        """
        log('POST request: url: {0}, payload: {1}'.format(url, payload))
        result = requests.post(url, json=payload, headers={"X-Atlassian-Token": "no-check"},
                               auth=HTTPBasicAuth(self.username, self.passwd))

        log('POST respond: status: {0}, content: {1}'.format(result.status_code, result.content))
        return result.content, result.status_code

    def send_put_request(self, url, payload):
        """Sends put request with spec header.

        Args:
            url (str): API URL to send comment.
            payload (dict): json to send.

        Returns:
            result.content (dict): Response content in json format.
            result.status_code (str): Response code.
        """
        log('PUT request: url: {0}, payload: {1}'.format(url, payload))
        result = requests.put(url, json=payload, headers={"X-Atlassian-Token": "no-check"},
                              auth=HTTPBasicAuth(self.username, self.passwd))
        log('PUT respond: staus: {0}, content: {1}'.format(result.status_code, result.content))
        return result.content, result.status_code

    def send_get_request(self, url, payload):
        """Sends get request with spec header.

        Args:
            url (str): API URL to send comment.
            payload (dict): json to send.

        Returns:
            result.content (dict): Response content in json format.
            result.status_code (str): Response code.
        """
        log('GET request: url: {0}, payload: {1}'.format(url, payload))
        result = requests.get(url, params=payload, headers={"X-Atlassian-Token": "no-check"},
                              auth=HTTPBasicAuth(self.username, self.passwd))
        log('GET respond: staus: {0}, content: {1}'.format(result.status_code, result.content))
        return result.content, result.status_code


if __name__ == '__main__':
    pass
