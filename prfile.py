#!/usr/bin/env python

import json
import logging
import os
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)
# noinspection PyShadowingBuiltins
class PRFile(object):
    """
    This class sends static checks results to pull request files.
    """
    fake_build_url = "http://jenkins.test"

    def set_data(self, checks_author="jenkins",
                 rest_api_link="/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/",
                 slug=None, project_name=None, pull_request_id=None):
        self.checks_author = checks_author
        self.rest_api_link = rest_api_link
        self.slug = slug
        self.project_name = project_name
        self.pull_request_id = pull_request_id
        return 0

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
        self.checks_author = "jenkins"
        self.rest_api_link = "/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/"
        self.slug = None
        self.project_name = None
        self.pull_request_id = None

    def generate_url(self):
        """This method is generate correct url for bitbucket api.

        Returns:
            url (str): API URL for adding comments.
        """
        if self.slug is None:
            logger.warning("Slug is not provided to class, trying to get it from environment variable.")
            slug = os.environ.get("SLUG", "TEST_KEY")
        else:
            slug = self.slug

        if self.project_name is None:
            logger.warning("Project name is not provided to class, trying to get it from environment variable.")
            project_name = os.environ.get("PROJECT", "TEST_REPO")
        else:
            project_name = self.project_name

        if self.pull_request_id is None:
            logger.warning("Pull request ID is not provided to class, trying to get it from environment variable.")
            pull_request_id = os.environ.get("PR_ID", "TEST_ID")
        else:
            pull_request_id = self.pull_request_id

        logger.debug("Generating URL with parameters slug: {0}, project: {1}, "
                     "pull request ID: {2}".format(slug, project_name, pull_request_id))
        url = self.base_api_link + self.rest_api_link
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
        result = (-1, 'Unknown error.')

        build_link = os.environ.get("BUILD_URL", PRFile.fake_build_url)
        text = ''
        try:
            for key in results.iterkeys():
                text += "{0} {1}".format(key, results[key])
        except Exception as e:
            logger.error("Error while generating comment message: {}".format(e))
        else:
            text += " You can find details via link {}".format(build_link)

            # Get result into temp variable, and check.
            code, message = self.check_comments_from_specific_author(self.checks_author)

            # if result is None, then we need to Post comment,
            # if result is Not none, then we need to PUT comment.
            if code != 0:
                result = (-1, message)
            elif code == 0 and not message:
                url = self.generate_url()
                payload = {"text": text, "anchor": {"path": self.checked_file}}
                result = self.send_post_request(url, payload)
            elif code == 0 and message:
                # And to PUT we need to pass additional parameters:
                # id of existing comment and it's version.
                url = self.generate_url()
                comment_id, comment_version = message
                self.base_api_link = '{0}/{1}'.format(url, comment_id)
                payload = {
                    "version": comment_version,
                    "text": text,
                    "anchor": {
                        "path": self.checked_file
                    }
                }
                result = self.send_put_request(self.base_api_link, payload)
        finally:
            return result

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
        logger.debug('Searching comments from {}'.format(author))
        result, comment_id_version = None, False
        code, message = self.get_all_comments_for_file()
        if code == -1:
            result = (-1, message)
        elif code == 0:
            comments = message
            for comment in comments:
                try:
                    if comment["author"]["name"] == author:
                        comment_id_version = (comment["id"], comment["version"])
                        logger.debug('Found comment for file {0} by author {1} with ID {}.'
                                     .format(self.checked_file, author, comment_id_version))
                        break
                except Exception as e:
                    logger.exception('Error occurred while processing with comments '
                                     'to file {0}.'.format(self.checked_file))
                    result = (-1, e)
                else:
                    if comment_id_version:
                        result = (0, comment_id_version)
        return result

    def get_all_comments_for_file(self):
        """Method for collecting all comments for specific file.

        Returns:
            result (dict of str): dictionary with comments.
        """
        logger.debug("Trying to get all comments for file {}...".format(self.checked_file))
        payload = {'path': self.checked_file}
        url = self.generate_url()
        code, message = self.send_get_request(url, payload)

        if code in [200, 204]:
            response = json.loads(message)
            result = (0, response["values"])
            logger.debug("Comments are successfully received.")
        elif code == -1:
            result = (-1, message)
            logger.error("Error occurred while getting comment for file {0}. Error: {1}".format(self.checked_file,
                                                                                                  message))
        else:
            result = (-1, '{0}: {1}'.format(code, message))
            logger.warning("Response is not 200 or 204. Code {0}: {1}".format(code, message))
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
        result = (-42, "Unknown.")
        logger.debug('POST request: url: {0}, payload: {1}'.format(url, payload))
        try:
            response = requests.post(url, json=payload, headers={"X-Atlassian-Token": "no-check"},
                                     auth=HTTPBasicAuth(self.username, self.passwd))
        except Exception as e:
            logger.exception("Error occurred while sending POST request.")
            result = (-1, e)
        else:
            logger.debug('POST respond: status: {0}, content: {1}'.format(response.status_code, response.content))
            result = response.status_code, response.content

        return result

    def send_put_request(self, url, payload):
        """Sends put request with spec header.

        Args:
            url (str): API URL to send comment.
            payload (dict): json to send.

        Returns:
            result.content (dict): Response content in json format.
            result.status_code (str): Response code.
        """
        result = (-42, "Unknown.")
        logger.debug('PUT request: url: {0}, payload: {1}'.format(url, payload))
        try:
            response = requests.put(url, json=payload, headers={"X-Atlassian-Token": "no-check"},
                                    auth=HTTPBasicAuth(self.username, self.passwd))
        except Exception as e:
            logger.exception("Error occurred while sending PUT request.")
            result = (-1, e)
        else:
            logger.debug('PUT respond: staus: {0}, content: {1}'.format(response.status_code, response.content))
            result = (response.status_code, response.content)
        return result

    def send_get_request(self, url, payload):
        """Sends get request with spec header.

        Args:
            url (str): API URL to send comment.
            payload (dict): json to send.

        Returns:
            result.content (dict): Response content in json format.
            result.status_code (str): Response code.
        """
        result = (-42, "Unknown.")
        logger.debug('GET request: url: {0}, payload: {1}'.format(url, payload))
        try:
            response = requests.get(url, params=payload, headers={"X-Atlassian-Token": "no-check"},
                                    auth=HTTPBasicAuth(self.username, self.passwd))
        except Exception as e:
            logger.exception("Error occurred while sending GET request.")
            result = (-1, e)
        else:
            logger.debug('GET respond: status: {0}, content: {1}'.format(response.status_code, response.content))
            result = (response.status_code, response.content)
        return result


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    pass
