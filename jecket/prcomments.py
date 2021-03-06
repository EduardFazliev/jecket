#!/usr/bin/env python
import json
import logging
import os

import jecket

logger = logging.getLogger(__name__)


class PRState(jecket.PRFile):
    rest_api_link = '/rest/build-status/1.0/commits/'

    def __init__(self):
        super(PRState, self).__init__('')

    def send_comment(self, comment):
        """This method sends comments to a pull-request at the generated URL.

        Args:
            comment (str): Text comment

        Returns:
            POST request containing URL and text comment / POST response
        """
        url = self.generate_url()
        payload = {'text': comment}
        return self.send_post_request(url, payload)

    def send_build_status(self, state, key, url_to_build):
        """This method sends build status to the generated URL.

        Args:
            state: build status (SUCCESS / FAILURE)
            key: build id
            url_to_build: url to build

        Returns:
            content (dict): Response content in json format.
            code (str): Response code.

        """
        if self.git_commit is not None:
            commit_hash = self.git_commit
        else:
            commit_hash = os.environ.get('GIT_COMMIT', 'TEST_HASH')
        url = self.base_api_link + PRState.rest_api_link + commit_hash
        logger.info('Sending build status for commit {}.'.format(commit_hash))
        payload = {
            'state': state,
            'key': key,
            'url': url_to_build
        }
        code, content = self.send_post_request(url, payload)
        logger.info('Sending finished. Result: status - {0}, content - {1}.'.format(code, content))
        return code, content


class PRCommits(jecket.PRFile):
    def __init__(self):
        super(PRCommits, self).__init__('')

    def generate_url(self):
        """This method generates the correct url for Bitbucket API.

        Returns:
            url (str): api url for adding comments.
        """
        if self.slug is None:
            logger.info('Slug is not provided to class, trying to get it from environment variable.')
            slug = os.environ.get('SLUG', 'TEST_KEY')
        else:
            slug = self.slug

        if self.project_name is None:
            logger.info('Project name is not provided to class, trying to get it from environment variable.')
            project_name = os.environ.get('PROJECT', 'TEST_REPO')
        else:
            project_name = self.project_name

        if self.pull_request_id is None:
            logger.info('Pull request ID is not provided to class, trying to get it from environment variable.')
            pull_request_id = os.environ.get('PR_ID', 'TEST_ID')
        else:
            pull_request_id = self.pull_request_id

        url = self.base_api_link + self.rest_api_link
        url = url.replace('{SLUG}', slug)
        url = url.replace('{PROJECT}', project_name)
        url = url.replace('{PRI}', pull_request_id)
        if url[-1] != '/':
            url += '/'
        url = '{0}commits'.format(url)
        logger.info('URL generated: {}'.format(url))
        return url

    def get_commits(self):
        """This method gets the list of commits id from the generated URL.

        Returns:
            result.commit (dict): Commit SHA value per commit id.

        """
        url = self.generate_url()
        payload = {'withcounts': 'false'}
        code, message = self.send_get_request(url, payload)
        if code in [200, 204]:
            commits = json.loads(message)
            result = [commit['id'] for commit in commits['values']]
        else:
            raise jecket.IncorrectJsonException(status=code, url=url, json=message)
        return result
