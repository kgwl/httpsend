import requests


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


def main():
    pass


if __name__ == '__main__':
    main()
