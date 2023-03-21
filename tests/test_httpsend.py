import base64
import os
import unittest
from unittest import TestCase
import mock
import httpsend
import random
import string
import urllib3
from aiohttp import ClientSession
from unittest.mock import Mock, AsyncMock


async def mock_response():
    response = Mock(spec=ClientSession)
    response.status = 200
    response.headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response.cookies = {'session_id': '123abc', 'username': 'johndoe'}
    response.text = AsyncMock(return_value='{"message": "Hello, World!"}')
    return response


class TestFormatResponse(unittest.IsolatedAsyncioTestCase):

    async def test_format_response_headers(self):
        response = await mock_response()
        result = await httpsend.format_response('all', response)
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['headers'], "Content-Type: application/json\nUser-Agent: "
                                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                                            "Chrome/58.0.3029.110 Safari/537.36\n")
        self.assertEqual(result['text'], '{"message": "Hello, World!"}')
        self.assertEqual(result['cookies'], "{'session_id': '123abc', 'username': 'johndoe'}")


class TestHttpsend(TestCase):
    dirs_to_remove = []

    @classmethod
    def setUpClass(cls):
        cls.url = 'https://example.com'
        cls.filename = 'input-files/test_read_urls.txt'
        urllib3.disable_warnings()

    @classmethod
    def tearDownClass(cls):
        for dir_name in cls.dirs_to_remove:
            os.removedirs(dir_name)

    def test_save(self):
        directory = 'output-files/'
        output_filename = base64.b64encode(self.url.encode('utf-8')).decode()
        path = directory + output_filename
        content = ''.join([random.choice(string.ascii_lowercase) for _ in range(10)])

        httpsend.save(path, content)
        file = open(path, 'r')
        result = file.read()
        file.close()

        self.assertEqual(result, content)

    def test_read_urls_file(self):
        urls = httpsend.read_urls(self.filename)
        self.assertEqual(type(urls), list)
        self.assertEqual(urls[0], 'https://example.com')
        self.assertEqual(urls[1], 'https://google.com')

    @mock.patch('builtins.open')
    def test_read_urls_open(self, mock_system):
        httpsend.read_urls(self.filename)
        mock_system.assert_called()

    def test_read_urls_single_url(self):
        urls = httpsend.read_urls(self.url)
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], self.url)

    def test_is_url_true(self):
        result = httpsend.is_url(self.url)
        self.assertTrue(result)

    def test_is_url_false(self):
        url = 'test'
        result = httpsend.is_url(url)
        self.assertFalse(result)

    def test_create_output_directory(self):
        # Make sure that all 'httpsend-output' directories in test directory are removed
        dir_name = os.path.abspath('.') + '/' + 'httpsend-output'
        result = httpsend.create_output_directory()
        self.dirs_to_remove.append(dir_name)

        self.assertEqual(result, dir_name)

    def test_create_output_directory_path(self):
        # Make sure that all 'httpsend-output' directories in test directory are removed
        dr = os.path.abspath('output-files')
        dir_name = dr + '/' + 'httpsend-output'
        result = httpsend.create_output_directory(dr)
        self.dirs_to_remove.append(dir_name)
        self.assertEqual(result, dir_name)

    def test_create_output_directory_multiple_output(self):
        dr = os.path.abspath('test-multiple-output')
        dir_name1 = dr + '/' + 'httpsend-output'
        dir_name2 = dr + '/' + 'httpsend-output1'
        result1 = httpsend.create_output_directory(dr)
        result2 = httpsend.create_output_directory(dr)

        self.dirs_to_remove.append(dir_name1)
        self.dirs_to_remove.append(dir_name2)

        self.assertEqual(result1, dir_name1)
        self.assertEqual(result2, dir_name2)

    def test_filter_status_codes_true(self):
        response_status_code = 200
        match_status_codes = [None, '200', '100,200,300', '200-300', '200,200,200', '200-200', '300-100']
        exclude_status_codes = [None, '100', '100,300,301,400', '300-400,500', '300,300', '400-400,400']
        for i in range(len(match_status_codes)):
            for j in range(len(exclude_status_codes)):
                status_codes = (exclude_status_codes[j], match_status_codes[i])
                result = httpsend.filter_status_codes(response_status_code, status_codes)
                self.assertTrue(result)

    def test_filter_status_codes_false(self):
        response_status_code = 200
        match_status_codes = ['100', '100,201,300,301', '300-400,100,500', None, '200']
        # exclude status codes overrides match status codes
        exclude_status_codes = ['200', '100,200,300', '100-300', '200-200', '200,200,200', '300-200']
        for i in range(len(match_status_codes)):
            for j in range(len(exclude_status_codes)):
                status_codes = (exclude_status_codes[j], match_status_codes[i])
                result = httpsend.filter_status_codes(response_status_code, status_codes)
                self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
