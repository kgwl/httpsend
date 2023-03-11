from urllib.parse import urlparse
import urllib3
import requests
import argparse
import validators
import os


def get_parser():
    """
    Parse command line arguments
    --------
    Returns:
        argparse: Command line arguments
    """

    parser = argparse.ArgumentParser(
        description='Send many http requests and save to files'
    )

    parser.add_argument(
        '-u',
        '--url',
        help='Target URL'
    )

    parser.add_argument(
        '-f',
        '--file',
        help='File witch target URLs'
    )

    parser.add_argument(
        '-X',
        '--method',
        default='GET',
        choices=['GET'],
        help='HTTP method to use'
    )

    parser.add_argument(
        '-E',
        '--element',
        choices=['text', 'headers', 'cookies'],
        default='all',
        help='HTTP element to save. All element are saved by default'
    )

    parser.add_argument(
        '-d',
        '--dir',
        help='Output directory'
    )

    return parser


def get(url, http_choice: str):
    """
    Sends http GET method and returns text, cookies and/or headers.

    Parameters:
    -----------
    url:
        URL where request should be sent.

    http_choice:
        What element of http should be return (cookies, headers, text or all of them).
    -----------
    Returns:
        dictionary: Selected http elements (cookies, headers,  text).
    """

    response = requests.get(url=url, verify=False)
    headers_result = ''
    cookies_result = ''
    text_result = ''

    if http_choice == 'headers' or http_choice == 'all':
        headers = response.headers
        for header in headers:
            headers_result += header + ': ' + headers[header] + '\n'

    if http_choice == 'cookies' or http_choice == 'all':
        cookies = response.cookies
        for cookie in cookies:
            cookies_result += cookie.name + '=' + cookie.value + '\n'

    if http_choice == 'text' or http_choice == 'all':
        text_result += response.text

    result = {'headers': headers_result, 'cookies': cookies_result, 'text': text_result}
    for key, value in result.copy().items():
        if value == '':
            del result[key]

    return result


def save(filename, content):
    file = open(filename, 'w')
    file.write(content)
    file.close()


def read_urls(filename: str):
    """
    Reads urls from file and return as list

    Parameters:
    -----------
    filename:
        full path to file with url

    -----------
    Returns:
        list: List of urls from file
    """

    result = []
    try:
        file = open(filename)
        for line in file.readlines():
            line = line.replace('\n', '')
            result.append(line)
        file.close()
    except FileNotFoundError:
        result.append(filename)

    return result


def is_url(url: str):
    """
    Checks if the URL is correct

    Parameters:
    -----------
    url:
        URL address to validate

    -----------
    Returns:
         bool: True if URL is valid
    """
    return validators.url(url)


def args_filter(parser, single_url, url_file):
    """
    From URL and FILE argument choose one which is not null. If both arguments are provided then program exits with
    an error.

    Parameters:
    -----------
    parser:
        ArgumentParser object

    single_url:
        URL parameter

    url_file:
        FILE parameter

    -----------
    Returns:
        str: Argument that is not null
    """
    if single_url is not None and url_file is not None:
        parser.error('You cannot pass [-u URL] and [-f FILE] arguments together')

    return single_url if single_url is not None else url_file


def create_output_directory(path: str = None):
    """
    Creates directory to store program output

    Parameters:
    -----------
    path:
        Path where directory should be created

    -----------
    Returns:
        str: Full path to the created directory
    """

    dir_name = 'httpsend-output'
    path = os.path.abspath('.') if path is None else path
    path = path + '/' + dir_name

    file_id = 0
    tmp_path = path
    while os.path.exists(path):
        file_id += 1
        path = tmp_path + str(file_id)

    os.makedirs(path)
    return path


def save_response(url, path, method, response):
    """
    Save response to file

    Parameters:
    -----------
    url:
        response URL

    path:
        Full path to save file

    method:
        used http method

    response:
        HTTP response

    """
    url = urlparse(url)
    domain = url.netloc
    url_path = url.path.replace('/', '_')
    filename = path + '/' + domain + url_path
    filename = os.path.abspath(filename)

    for key in response.keys():
        name = filename + '.' + method + '.' + key
        print('saved  ', name)
        save(name, response[key])


def main():
    parser = get_parser()
    args = parser.parse_args()
    element = args.element
    method = args.method
    filename = args_filter(parser, args.url, args.file)
    urls = read_urls(filename)
    path = create_output_directory(args.dir)
    urllib3.disable_warnings()
    for url in urls:
        if not is_url(url):
            print('\033[91m' + url + ' is not valid' + '\033[0m')
            continue

        if method == 'GET':
            result = get(url, element)
            save_response(url, path, method, result)


if __name__ == '__main__':
    main()
