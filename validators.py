import re

regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# print(re.match(regex, "http://www.example.com") is not None)  # True
# print(re.match(regex, "example.com") is not None)            # False


def validate_url(url):
    if (re.match(regex, url) is not None):
        return True
    else:
        return False
