from urllib.parse import urlparse
import urllib3
import argparse
import validators
import os
from http import HTTPStatus
import asyncio
from aiohttp import ClientSession, TCPConnector


def get_parser():
    """
    Parse command line arguments
    --------
    Returns:
        argparse: Command line arguments
    """

    parser = argparse.ArgumentParser(
        prog='httpsend',
        description='Send many http requests and save to files',
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50),
        add_help=False
    )

    filter_options = parser.add_argument_group('filter options')
    match_options = parser.add_argument_group('match options')

    parser.add_argument(
        '--help',
        action='help',
        default=argparse.SUPPRESS,
        help='Show this help message and exit')

    parser.add_argument(
        '-u',
        dest='url',
        metavar='URL',
        help='Target URL'
    )

    parser.add_argument(
        '-f',
        metavar='FILE',
        dest='file',
        help='File with target URLs'
    )

    parser.add_argument(
        '-X',
        dest='method',
        default='GET',
        choices=['GET'],
        help='HTTP method to use. Default: GET'
    )

    parser.add_argument(
        '-E',
        dest='element',
        choices=['text', 'headers', 'cookies'],
        default='all',
        help='HTTP element to save. All element are saved by default'
    )

    parser.add_argument(
        '-d',
        dest='dir',
        metavar='DIR',
        help='Output directory'
    )

    parser.add_argument(
        '-H',
        dest='header',
        metavar='HEADER',
        help='Http headers to use'
    )

    filter_options.add_argument(
        '-fs',
        metavar='CODE',
        dest='exclude_status_code',
        help='Exclude HTTP status code. Comma separated list or range e.q 200,300-400. Overrides match-status-code'
    )

    match_options.add_argument(
        '-ms',
        metavar='CODE',
        dest='match_status_code',
        help='Match HTTP status codes. Comma separated list or range e.q 200,300-400.'
    )

    return parser


async def format_response(element: str, response: ClientSession.get):
    """
    Get from response only selected items

    Parameters:
    -----------
    http_choice:
        What element of http should be return (cookies, headers, text or all of them).

    response:
        aiohttp.ClientSession.get object
    -----------
    Returns:
        dictionary: Selected http elements (cookies, headers,  text).
    """

    headers_result = ''
    cookies_result = ''
    text_result = ''
    status_code = response.status

    if element == 'headers' or element == 'all':
        headers = response.headers
        for header in headers:
            headers_result += header + ': ' + headers[header] + '\n'

    if element == 'cookies' or element == 'all':
        cookies = response.cookies
        cookies_result = str(cookies)

    if element == 'text' or element == 'all':
        text_result += await response.text()

    result = {'headers': headers_result, 'cookies': cookies_result, 'text': text_result, 'status_code': status_code}
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
        response URL7

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
    status_code = response['status_code']
    del response['status_code']

    for key in response.keys():
        name = filename + '.' + method + '.' + key
        print('[' + str(status_code) + ']  ' + name + '\033[92m' + ' saved' + '\033[0m')
        save(name, response[key])


def filter_status_codes(response_status_code: int, user_status_codes: tuple):
    """
    Check if response status code match to status codes filtered by user

    Parameters:
    -----------
    user_status_codes:
        Tuple of status codes to exclude and status codes that should match (exclude status codes, match status codes)

    -----------
    Returns:
        bool: True if status code matches
    """
    http_status_codes = [code.value for code in HTTPStatus]

    def get_codes(status_codes):
        result = []
        for code in status_codes:
            if len(code) == 1:
                if int(code[0]) in http_status_codes:
                    result.append(int(code[0]))
            if len(code) == 2:
                max_status_code, min_status_code = max(int(code[0]), int(code[1])), min(int(code[0]), int(code[1]))
                result += [n for n in http_status_codes if min_status_code <= n <= max_status_code]
        return result

    exclude_status_code = [code.split('-') for code in user_status_codes[0].split(',')] if user_status_codes[0] is not None else []
    match_status_code = [code.split('-') for code in user_status_codes[1].split(',')] if user_status_codes[1] is not None else []

    http_status_codes = get_codes(match_status_code) if len(match_status_code) > 0 else http_status_codes
    exclude_status_code = get_codes(exclude_status_code)
    http_status_codes = list(set(http_status_codes) - set(exclude_status_code))

    return response_status_code in http_status_codes


def get_headers(headers):
    headers_dict = {}
    try:
        headers_list = headers.split(',')
        for header in headers_list:
            key, value = header.split(':')
            headers_dict[key.strip()] = value.strip()
    except ValueError:
        return {}
    return headers_dict


def get_args():
    parser = get_parser()
    args = parser.parse_args()
    element = args.element
    method = args.method
    status_codes = (args.exclude_status_code, args.match_status_code)
    filename = args_filter(parser, args.url, args.file)
    urls = read_urls(filename)
    path = create_output_directory(args.dir)
    headers = get_headers(args.header)

    return {'element': element, 'method': method, 'status_codes': status_codes, 'urls': urls, 'path': path, 'headers': headers}


async def send_request(args, url):
    async with ClientSession(headers=args['headers'], connector=TCPConnector(ssl=False)) as session:
        if args['method'] == 'GET':
            async with await session.get(url=url) as response:
                result = await format_response(args['element'], response)
                if filter_status_codes(result['status_code'], args['status_codes']):
                    save_response(url, args['path'], args['method'], result)
                else:
                    print('\033[93m' + '[' + str(response.status) + '] ' + url + ' filtered' + '\033[0m')


def main():

    urllib3.disable_warnings()
    args = get_args()

    loop = asyncio.get_event_loop()
    tasks = []

    for url in args['urls']:
        if not is_url(url):
            print('\033[91m' + url + ' is not valid' + '\033[0m')
            continue
        task = asyncio.ensure_future(send_request(args, url))
        tasks.append(task)

    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    main()
