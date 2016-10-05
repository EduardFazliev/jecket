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
    config = '/tmp/jecket.conf'

    def __init__(
            self, checked_file,  base_api_link=None, username=None, passwd=None, git_commit=None, slug=None, project_name=None,
            pull_request_id=None, check_author='jenkins', build_url=None
        ):
        """
        Args:
            base_api_link (str): link to bitbucket's api service.
            checked_file (str): path to file, that is going
                to be checked with static checks.
            username (str): login for basic auth.
            passwd (str): password for basic auth.

        """

        self._base_api_link = base_api_link
        self._username = username
        self._passwd = passwd
        self.checked_file = checked_file
        self._check_author = check_author
        self.rest_api_link = '/rest/api/1.0/projects/{SLUG}/repos/{PROJECT}/pull-requests/{PRI}/'
        self._slug = slug
        self._project_name = project_name
        self._pull_request_id = pull_request_id
        self._git_commit = git_commit
        self._build_url = build_url
    
    @property
    def base_api_link(self):
        if self._base_api_link is not None:
            return self._base_api_link
        else:
            return os.environ.get('BASE_API_LINK', '0')

    @base_api_link.setter
    def base_api_link(self, value):
        self._base_api_link = value

    @property
    def username(self):
        if self._username is not None:
            return self._username
        else:
            return os.environ.get('USERNAME', '0')

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def passwd(self):
        if self._passwd is not None:
            return self._passwd
        else:
            return os.environ.get('PASSWD', '0')
    
    @passwd.setter
    def passwd(self, value):
        self._passwd = value

    @property
    def check_author(self):
        return self._check_author

    @check_author.setter
    def check_author(self, value):
        self._check_author = value

    @property
    def slug(self):
        if self._slug is not None:    
            return self._slug
        else:
            return os.environ.get('SLUG','0')

    @slug.setter
    def slug(self, value):
        self._slug = value

    @property
    def project_name(self):
        if self._project_name is not None:
            return self._project_name
        else:
            return os.environ.get('PROJECT_NAME', '0')

    @project_name.setter
    def project_name(self, value):
        self._project_name = value

    @property
    def pull_request_id(self):
        if self._pull_request_id is not None:
            return self._pull_request_id
        else:
            return os.environ.get('PULL_REQUEST_ID', '0')

    @pull_request_id.setter
    def pull_request_id(self, value):
        self._pull_request_id = value

    @property
    def git_commit(self):
        if self._git_commit is not None:
            return self._git_commit
        else:
            return os.environ.get('GIT_COMMIT', '0')

    @git_commit.setter
    def git_commit(self, value):
        self._git_commit = value

    @property
    def build_url(self):
        if self._git_commit is not None:
            return self._build_url
        else:
            return os.environ.get('BUILD_URL', 'No URL defined.')

    @build_url.setter
    def build_url(self, value):
        self._build_url = value

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
        logger.debug('Generating URL with parameters slug: {0}, project: {1}, '
                     'pull request ID: {2}'.format(self.slug, self.project_name, self.pull_request_id))
        url = self.base_api_link + self.rest_api_link
        url = url.replace('{SLUG}', self.slug)
        url = url.replace('{PROJECT}', self.project_name)
        url = url.replace('{PRI}', self.pull_request_id)
        # We need to be sure, that URL ends with slash
        if url[-1] != '/':
            url += '/'
        url = '{0}comments'.format(url)
        return url

    def send_static_check_results(self, static_check_result):
        """Method sends static check results (PMD and checkstyle
        for now) as a comment for specific file in commit.

        Args:
            static_check_result (dict of title: value):
                {
                    title (str): value (str)
                }
                title: Violation description.
                value: Number of violations.

        Returns:
            content (str): Respond's payload.
            code (int): Response's code.
        """
        logger.debug('Check results will be used to generate comment message. Results: {0}'.format(static_check_result))
        # TODO We need to implement build_link as property, like other stuff.
        logger.debug('Get build link from environment variable. Result: {0}'.format(self.build_url))
        text = ''
        logger.debug('Initializing comment text...')
        try:
            for key in static_check_result.iterkeys():
                text += '{0} {1}, '.format(key, static_check_result[key])
        except (KeyError, ValueError):
            logger.exception('Error while generating comment message: {0}'.format(e))
            logger.info('Error occurred while generating comment text...')
        else:
            text += ' You can find details via link {0}'.format(self.build_url)

            # Get result into temp variable, and check.
            answer = self.comment_request_type()
            code = answer[0]

            if code == 1:
                logger.debug('Adding new comment:')
                url = self.generate_url()
                payload = {'text': text, 'anchor': {'path': self.checked_file}}
                return self.send_post_request(url, payload)
            elif code == 0:
                logger.debug('Editing existing comment.')
                # To PUT we need to pass additional parameters:
                # id of existing comment and it's version.
                url = self.generate_url()
                _, comment_id, comment_version = answer
                link = '{0}/{1}'.format(url, comment_id)
                payload = {
                    'version': comment_version,
                    'text': text,
                    'anchor': {
                        'path': self.checked_file
                    }
                }
                return self.send_put_request(link, payload)
            else:
                return -1

    def compare_authors(self, comments):
        """Method compares all given comments author with self.check_author.

        Args:
            comments (dict of str): dictionary with information about all comments.

        Returns:
            1 if there is no comments from self.check_author and we need to add new comment and send post request,
            (0, comment_id, comment_version) (tuple of (int, str, str)): If there is comment from self.check_author,
                and this means that we need to edit old comment by sending put request and for this we need
                comment_id and comment_version,
            -1 if there was error, traceback are logged by logger.exception.
        """
        for comment in comments:
            # We do not want to raise exception here. So catch as much as possible.
            try:
                if comment['author']['name'] == self.check_author:
                    comment_id_version = (comment['id'], comment['version'])
                    logger.debug('Found comment for file {0} by author {1} with ID {2}.'
                                 .format(self.checked_file, self.check_author, comment_id_version))
                    return 0, comment['id'], comment['version']
                return 1
            except (KeyError, ValueError):
                logger.exception('Error occurred while comparing authors.')
                return -1

    def comment_request_type(self):
        """Method searches for comments from specific author.

        Args:
            author (str): Username of author.

        Returns:
            comment_id (str): 'Error' if error occurred while searching
            for comments from specific author or comment ID of first
            found comment or None if nothing is found and there is no
            errors.
        """
        logger.debug('Searching comments from {}'.format(self.check_author))
        # Get all comments for file. If success, we will get tuple (0, messages), where 0 is success code,
        # and message can be list of comments or empty list.
        result = self.get_all_comments_for_file()
        code = result[0]
        if code == -1:
            logger.error('Comments checking for author {0} failed.'.format(self.check_author))
            return -1

        if code == 0:
            _, comments = result
            logger.debug('Trying to find comment by {0}'.format(self.check_author))
            return self.compare_authors(comments)

    def get_all_comments_for_file(self):
        """Method for collecting all comments for specific file.

        Returns:
            Tuple (0, comments) where comments is dict if comments are successfully received,
            -1 otherwise.
        """
        logger.debug('Trying to get all comments for file {0}...'.format(self.checked_file))
        payload = {'path': self.checked_file}
        url = self.generate_url()
        code, message = self.send_get_request(url, payload)

        if code in [200, 204]:
            # First let's try decode received json.
            try:
                response = json.loads(message)
            except ValueError:
                # If ValueError is raised - return error code -1 and error message.
                logger.exception('Incorrect json received. Can not decode json.')
                logger.info('Can not decode json.')
                return -1
            # If json successfully decoded, we need to get value of 'values' key.
            try:
                comments = response['values']
            except KeyError:
                # If KeyError is raised, then return error code -1 and error message.
                logger.exception('No "value" key in received json.')
                logger.info('Error in received json.')
                return -1
            else:
                # If everything is OK, we need to return list of comments for file.
                logger.debug('Comments are successfully received, result: {0}.'.format(comments))
                return 0, comments
        elif code == -1:
            logger.error('Error occurred while getting comment for file {0}. Error: {1}'.format(self.checked_file,
                                                                                                message))
            return -1
        else:
            # If some internal programm error occurred, then return error code -1 and internal error message.
            logger.warning('Response is not 200 or 204. Code {0}: {1}, comments are NOT received.'.format(code, message))
            return -1

    # TODO Need refactoring. We need to make some more return-points, and make this function more readable.
    # TODO Add unit tests
    def send_post_request(self, url, payload):
        """Sends post request with spec header.

        Args:
            url (str): API URL to send comment.
            payload (dict): json to send.

        Returns:
            result.content (dict): Response content in json format.
            result.status_code (str): Response code.
        """
        result = (-42, 'Unknown.')
        logger.debug('POST request: url: {0}, payload: {1}'.format(url, payload))
        try:
            response = requests.post(url, json=payload, headers={'X-Atlassian-Token': 'no-check'},
                                     auth=HTTPBasicAuth(self.username, self.passwd))
        except Exception as e:
            logger.exception('Error occurred while sending POST request.')
            result = (-1, e)
        else:
            logger.debug('POST respond: status: {0}, content: {1}'.format(response.status_code, response.content))
            result = response.status_code, response.content

        return result

    # TODO Need refactoring. We need to make some more return-points, and make this function more readable.
    # TODO Add unit tests
    def send_put_request(self, url, payload):
        """Sends put request with spec header.

        Args:
            url (str): API URL to send comment.
            payload (dict): json to send.

        Returns:
            result.content (dict): Response content in json format.
            result.status_code (str): Response code.
        """
        result = (-42, 'Unknown.')
        logger.debug('PUT request: url: {0}, payload: {1}'.format(url, payload))
        try:
            response = requests.put(url, json=payload, headers={'X-Atlassian-Token': 'no-check'},
                                    auth=HTTPBasicAuth(self.username, self.passwd))
        except Exception as e:
            logger.exception('Error occurred while sending PUT request.')
            result = (-1, e)
        else:
            logger.debug('PUT respond: status: {0}, content: {1}'.format(response.status_code, response.content))
            result = (response.status_code, response.content)
        finally:
            return result

    # TODO Need refactoring. We need to make some more return-points, and make this function more readable.
    # TODO Add unit tests
    def send_get_request(self, url, payload):
        """Sends get request with spec header.

        Args:
            url (str): API URL to send comment.
            payload (dict): json to send.

        Returns:
            result.content (dict): Response content in json format.
            result.status_code (str): Response code.
        """
        result = (-42, 'Unknown.')
        logger.debug('GET request: url: {0}, payload: {1}'.format(url, payload))
        try:
            response = requests.get(url, params=payload, headers={'X-Atlassian-Token': 'no-check'},
                                    auth=HTTPBasicAuth(self.username, self.passwd))
        except Exception as e:
            logger.exception('Error occurred while sending GET request.')
            result = (-1, e)
        else:
            logger.debug('GET respond: status: {0}, content: {1}'.format(response.status_code, response.content))
            result = (response.status_code, response.content)
        finally:
            return result


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    pass
