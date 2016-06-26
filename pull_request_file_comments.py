#!/usr/bin/env python

import json
import os
from requests.auth import HTTPBasicAuth
import requests
import sys


# noinspection PyShadowingBuiltins
class SendResultsToPullRequestFiles(object):
    """
    This class sends static checks results to pull request files.
    """
    checks_author = 'jenkins'

    def __init__(self, base_api_link, checked_file, username, passwd):
        """Args:
            base_api_link (str): link to bitbucket's api service.
            checked_file (str): path to file, that is going
                to be checked with static checks.
            username (str): login for basic auth.
            passwd (str): passwd for basic auth.
        """
        self.username = username
        self.passwd = passwd
        self.base_api_link = base_api_link
        self.checked_file = checked_file
        self.api_link = ''

    def generate_url(self):
        """This method is generate correct url for bitbucket api.

        Returns:
            url (str): api url for adding comments.
        """
        slug = os.environ.get("SLUGNAME", 'DOCM')
        project_name = os.environ.get("PROJECT_NAME", 'infotech-ansible')
        pull_request_id = os.environ.get("PRI", '9')
        
        url = self.base_api_link
        url = url.replace('{SLUG}', slug)
        url = url.replace('{PROJECT}', project_name)
        url = url.replace('{PRI}', pull_request_id)
        if url[-1] != '/':
            url += '/'
        url = '{0}comments'.format(url)
        return url

    def send_static_check_results(self):
        text_vars = {
            'checkstyle': os.environ.get("CHECKSTYLE_COUNT", '-1'),
            'pmd': os.environ.get("PMD_COUNT", '-1'),
            'build_link': os.environ.get("BUILD_self.base_api_link", 'http://jenkins.test')
        }
        text = "PMD Errors: {0}, Checkstyle Errors: {1}," \
               "You can find details via link {2}".format(
                   text_vars['pmd'],
                   text_vars['checkstyle'],
                   text_vars['build_link']
               )

        # Get result into temp variable, and check.
        temp = self.check_comments_from_specific_author(
            SendResultsToPullRequestFiles.checks_author
        )
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
            content, code = self.send_put_request(
                self.base_api_link,
                payload
            )
        return content, code

    def check_comments_from_specific_author(self, author):
        comment_id_version = None
        comments = self.get_all_comments_for_file()
        for comment in comments:
            if comment["author"]["name"] == author:
                comment_id_version = (comment['id'], comment['version'])
                break
        return comment_id_version

    def get_all_comments_for_file(self):
        payload = {'path': self.checked_file}
        url = self.generate_url()
        content, code = self.send_get_request(url, payload)
        response = json.loads(content)

        if code == 200:
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
        result = requests.post(
            url,
            json=payload,
            headers={"X-Atlassian-Token": "no-check"},
            auth=HTTPBasicAuth(
                self.username,
                self.passwd
            )
        )
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
        result = requests.put(
            url,
            json=payload,
            headers={"X-Atlassian-Token": "no-check"},
            auth=HTTPBasicAuth(
                self.username,
                self.passwd
            )
        )
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
        result = requests.get(
            url,
            params=payload,
            headers={"X-Atlassian-Token": "no-check"},
            auth=HTTPBasicAuth(
                self.username,
                self.passwd
            )
        )
        return result.content, result.status_code


def main():
    pr_test = SendResultsToPullRequestFiles(
        base_api_link=sys.argv[1],
        checked_file=sys.argv[2],
        username='jenkins',
        passwd='jenkins'
    )
    result = pr_test.send_static_check_results()
    print result


if __name__ == '__main__':
    main()
