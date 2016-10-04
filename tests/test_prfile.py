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
        os.environ['BUILD_URL'] = 'http://build.url'

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
        expected_result = -1
        get.return_value = (502, '{"err": "Error."}')
        generate.return_value = 'http://somelink'
        prfile = PRFile('somefile')
        result = prfile.get_all_comments_for_file()
        self.assertEqual(result, expected_result)

    @mock.patch('jecket.PRFile.generate_url')
    @mock.patch('jecket.PRFile.send_get_request')
    def test_get_all_comment_for_file_error(self, get, generate):
        expected_result = -1
        get.return_value = (-1, 'error')
        generate.return_value = 'http://somelink'
        prfile = PRFile('somefile')
        result = prfile.get_all_comments_for_file()
        self.assertEqual(result, expected_result)

    @mock.patch('jecket.PRFile.generate_url')
    @mock.patch('jecket.PRFile.send_get_request')
    def test_get_all_comment_for_file_no_value_key(self, get, generate):
        expected_result = -1
        get.return_value = (200, '{"other_key": "Some comment."}')
        generate.return_value = 'http://somelink'
        prfile = PRFile('somefile')
        result = prfile.get_all_comments_for_file()
        self.assertEquals(result, expected_result)

    def test_compare_author_new_comment_required(self):
        comments = [
            {
                'author':
                    {
                        'name': 'Vasyan'
                    },
                'id': '0',
                'version': '13'
            },
            {
                'author':
                    {
                        'name': 'Kolyan'
                    },
                'id': '1',
                'version': '1'
            }
        ]
        expected_result = 1
        prfile = PRFile('somefile')
        result = prfile.compare_authors(comments)
        self.assertEquals(expected_result, result)

    def test_compare_author_comment_by_spec_author_is_exist(self):
        comments = [
            {
                'author':
                    {
                        'name': 'Vasyan'
                    },
                'id': '0',
                'version': '13'
            },
            {
                'author':
                    {
                        'name': 'Kolyan'
                    },
                'id': '1',
                'version': '1'
            }
        ]
        expected_result = (0, '0', '13')
        prfile = PRFile('somefile')
        prfile.check_author = 'Vasyan'
        result = prfile.compare_authors(comments)
        self.assertEquals(expected_result, result)

    def test_compare_author_key_error(self):
        comments = [
            {
                'author':
                    {
                        'author_name': 'Vasyan'
                    },
                'id': '0',
                'version': '13'
            },
            {
                'author':
                    {
                        'name': 'Kolyan'
                    },
                'id': '1',
                'version': '1'
            }
        ]
        expected_result = -1
        prfile = PRFile('somefile')
        prfile.check_author = 'Vasyan'
        result = prfile.compare_authors(comments)
        self.assertEquals(expected_result, result)

    @mock.patch('jecket.PRFile.get_all_comments_for_file')
    @mock.patch('jecket.PRFile.compare_authors')
    @mock.patch('jecket.PRFile.send_put_request')
    def test_send_static_check_results_0(self, mock_send_put_request, mock_compare_authors, mock_get_all_comments_for_file):
        results = {'some_error': '5'}
        expected_result = ('200', 'OK')
        mock_send_put_request.return_value = ('200', 'OK')
        mock_compare_authors.return_value = (0, 'some_id', 'some_version')
        mock_get_all_comments_for_file.return_value = (0, 'comments')
        prfile = PRFile('somefile')
        result = prfile.send_static_check_results(results)
        self.assertEquals(result, expected_result)



if __name__ == '__main__':
    unittest.main()
