import requests
import argparse
import validators


def parse_args():
    """
    Parse command line arguments
    --------
    Returns:b
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

    return parser.parse_args()


def get(url, http_choice: str):
    """
    Sends http GET method and returns text, cookies and/or headers.

    Parameters:
    -----------
    url:
        URL where request should be sent.

    http_choice:
        What element of http should be return (cookies, headers, text or all of them).
        nargs=1,
    -----------
    Returns:
        dictionary: Selected http elements (cookies, headers,  text).
    """

    response = requests.get(url=url)
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

    Returns:
        bool: True if URL is valid
    """
    return validators.url(url)


def main():
    pass


if __name__ == '__main__':
    main()
