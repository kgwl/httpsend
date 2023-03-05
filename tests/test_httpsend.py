import base64
import os
from unittest import TestCase
from unittest.mock import patch
import httpsend
import random
import string


class TestHttpsend(TestCase):

    dirs_to_remove = []

    @classmethod
    def setUpClass(cls):
        cls.url = 'https://example.com'
        cls.filename = 'input-files/test_read_urls.txt'

    @classmethod
    def tearDownClass(cls):
        for dir_name in cls.dirs_to_remove:
            os.removedirs(dir_name)

    def test_get_type(self):
        self.response = httpsend.get(url=self.url, http_choice='all')
        self.assertEqual(type(self.response), dict)

    def test_get_choice(self):
        self.response = httpsend.get(url=self.url, http_choice='text')
        self.assertEqual(list(self.response.keys())[0], 'text')

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

    @patch('builtins.open')
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
