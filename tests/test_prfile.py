import os
import unittest

import mock

import jecket
from jecket import PRFile

base_api_link = 'http://some.link'
username = 'user'
passwd = 'passwd'
slug = 'test_slug'
project_name = 'test_pr_name'
pull_request_id = '1'
git_commit = '2'


class TestPRFile(unittest.TestCase):
    def setUp(self):
        os.environ['SLUG'] = slug
        os.environ['PROJECT_NAME'] = project_name
        os.environ['PULL_REQUEST_ID'] = pull_request_id 
        os.environ['BASE_API_LINK'] = base_api_link
        os.environ['USERNAME'] = username
        os.environ['PASSWD'] = passwd

    def test_generate_url_class_variables(self):
        expected_result = 'http://some.link/rest/api/1.0/projects/{0}/repos/{1}/pull-requests/{2}/comments'.format(slug, project_name, pull_request_id)
        prfile = PRFile(
            'somefile', base_api_link=base_api_link, username=username, passwd=passwd, git_commit=git_commit, slug=slug,
            project_name=project_name, pull_request_id=pull_request_id
        )
        result = prfile.generate_url()
        self.assertEqual(result, expected_result)

    def test_generate_url_env_variables(self):
        expected_result = 'http://some.link/rest/api/1.0/projects/{0}/repos/{1}/pull-requests/{2}/comments'.format(slug, project_name, pull_request_id)
        prfile = PRFile('somefile')
        result = prfile.generate_url()
        self.assertEqual(result, expected_result)

    @mock.patch('jecket.PRFile.generate_url')
    @mock.patch('jecket.PRFile.send_get_request')
    def test_get_all_comment_for_file_200(self, get, generate):
        expected_result = (0, 'Some comment.')
        get.return_value = (200, '{"values": "Some comment."}')
        generate.return_value = 'http://somelink'
        prfile = PRFile('somefile')
        result = prfile.get_all_comments_for_file()
        self.assertEqual(result, expected_result)
        
    @mock.patch('jecket.PRFile.generate_url')
    @mock.patch('jecket.PRFile.send_get_request')
    def test_get_all_comment_for_file_502(self, get, generate):
        expected_result = (-1, '502: {"err": "Error."}')
        get.return_value = (502, '{"err": "Error."}')
        generate.return_value = 'http://somelink'
        prfile = PRFile('somefile')
        result = prfile.get_all_comments_for_file()
        self.assertEqual(result, expected_result)

    @mock.patch('jecket.PRFile.generate_url')
    @mock.patch('jecket.PRFile.send_get_request')
    def test_get_all_comment_for_file_error(self, get, generate):
        expected_result = (-1, 'error')
        get.return_value = (-1, 'error')
        generate.return_value = 'http://somelink'
        prfile = PRFile('somefile')
        result = prfile.get_all_comments_for_file()
        self.assertEqual(result, expected_result)

    @mock.patch('jecket.PRFile.generate_url')
    @mock.patch('jecket.PRFile.send_get_request')
    def test_get_all_comment_for_file_no_value_key(self, get, generate):
        expected_result = (-1,'No "value" key in received json.')
        get.return_value = (200, '{"other_key": "Some comment."}')
        generate.return_value = 'http://somelink'
        prfile = PRFile('somefile')
        result = prfile.get_all_comments_for_file()


if __name__ == '__main__':
    unittest.main()
