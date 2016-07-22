#!/usr/bin/env python

import json
import logging
import os
import requests
from requests.auth import HTTPBasicAuth


logger = logging.getLogger(__name__)


class PRFile(object):
    """
    This class sends static checks results to pull request files.
    """
    fake_build_url = 'http://jenkins.test'
    config = '/tmp/jecket.conf'

    def set_data(self, checks_author="jenkins",
                 rest_api_link="/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/",
                 slug=None, project_name=None, pull_request_id=None):
        self.checks_author = checks_author
        self.rest_api_link = rest_api_link
        self.slug = slug
        self.project_name = project_name
        self.pull_request_id = pull_request_id
        return 0

    def __init__(self, checked_file):
        """Args:
            base_api_link (str): link to bitbucket's api service.
            checked_file (str): path to file, that is going
                to be checked with static checks.
            username (str): login for basic auth.
            passwd (str): password for basic auth.
        """

        self.config_generator = self.get_config()
        self.base_api_link = self.config_generator.next()
        self.username = self.config_generator.next()
        self.passwd = self.config_generator.next()
        self.checked_file = checked_file
        self.checks_author = "jenkins"
        self.rest_api_link = "/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/"
        self.slug = None
        self.project_name = None
        self.pull_request_id = None

    @staticmethod
    def get_config():
        with open(PRFile.config, 'r') as f:
            for line in f:
                yield line.replace('\n', '')

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
        result = (-42, 'Unknown error.')
        logger.debug('Check results will be used to generate comment message. Results: {0}'.format(results))
        build_link = os.environ.get("BUILD_URL", PRFile.fake_build_url)
        logger.debug('Get build link from environment variable. Result: {0}'.format(build_link))
        text = ''
        logger.debug('Initializing comment text...')
        try:
            for key in results.iterkeys():
                text += "{0} {1}".format(key, results[key])
                logger.debug('Generating comment text... current text: {0}'.format(text))
        except Exception as e:
            logger.exception("Error while generating comment message: {0}".format(e))
            logger.info('Error occurred while generating comment text...')
        else:
            text += " You can find details via link {0}".format(build_link)

            # Get result into temp variable, and check.
            code, message = self.check_comments_from_specific_author(self.checks_author)
            logger.debug('Checking comments from specific author, and result is {0}, '
                         'message is {1}'.format(code, message))
            # if result is None, then we need to Post comment,
            # if result is Not none, then we need to PUT comment.
            if code == 0 and message == 'New comment required.':
                url = self.generate_url()
                payload = {"text": text, "anchor": {"path": self.checked_file}}
                logger.debug('Code is 0 and message is "False". Sending post request with payload: {0}'.format(payload))
                result = self.send_post_request(url, payload)
            elif code == 0:
                # And to PUT we need to pass additional parameters:
                # id of existing comment and it's version.
                url = self.generate_url()
                comment_id, comment_version = message
                link = '{0}/{1}'.format(url, comment_id)
                payload = {
                    "version": comment_version,
                    "text": text,
                    "anchor": {
                        "path": self.checked_file
                    }
                }
                logger.debug('Code is 0 and message is not "New comment required": '
                             'Sending put request with payload: {0}'.format(payload))
                result = self.send_put_request(link, payload)
            else:
                result = (-1, message)
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
        # Initialize some variables
        result = (-42, 'Unknown Error')
        comment_id_version = None

        # Get all comments for file. If success, we will get tuple (0, messages), where 0 is success code,
        # and message can be list of comments or empty list.
        code, message = self.get_all_comments_for_file()
        if code == -1:
            result = (-1, message)
        elif code == 0 and message:
            logger.debug('Comments list is not empty, and code is 0. Trying to find comment by {0}'.format(author))
            comments = message
            try:
                for comment in comments:
                    if comment["author"]["name"] == author:
                        comment_id_version = (comment["id"], comment["version"])
                        logger.debug('Found comment for file {0} by author {1} with ID {2}.'
                                     .format(self.checked_file, author, comment_id_version))
                        break
            except Exception as e:
                logger.exception('Error occurred while iterating over comments for file {0}'
                                 .format(self.checked_file))
                result = (-1, e)
            else:
                if comment_id_version is not None:
                    logger.debug('Sending id and version of comment {0} '
                                 'from author {1}.'.format(comment_id_version, author))
                    result = (0, comment_id_version)
                else:
                    logger.debug("No comment found for author {0}. "
                                 "Sending signal 'New comment required'.".format(author))
                    result = (0, 'New comment required.')

        elif code == 0 and not message:
            logger.debug("No comments found for file {0}. Sending signal "
                         "'New comment required'.".format(self.checked_file))
            result = (0, 'New comment required.')
        return result

    def get_all_comments_for_file(self):
        """Method for collecting all comments for specific file.

        Returns:
            result (dict of str): dictionary with comments.
        """
        logger.debug("Trying to get all comments for file {0}...".format(self.checked_file))
        payload = {'path': self.checked_file}
        url = self.generate_url()
        code, message = self.send_get_request(url, payload)

        if code in [200, 204]:
            response = json.loads(message)
            result = (0, response["values"])
            logger.debug("Comments are successfully received, result: {0}.".format(result))
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
            logger.debug('PUT respond: status: {0}, content: {1}'.format(response.status_code, response.content))
            result = (response.status_code, response.content)
        finally:
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
        finally:
            return result


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    pass
