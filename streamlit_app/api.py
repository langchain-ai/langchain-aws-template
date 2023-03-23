import json
from urllib.parse import urlparse, urlencode, parse_qs

import re

import requests
from boto3 import Session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


def signing_headers(method, url_string, body):
    region = re.search("execute-api.(.*).amazonaws.com", url_string).group(1)
    url = urlparse(url_string)
    path = url.path or '/'
    querystring = ''
    if url.query:
        querystring = '?' + urlencode(
            parse_qs(url.query, keep_blank_values=True), doseq=True)

    safe_url = url.scheme + '://' + url.netloc.split(
        ':')[0] + path + querystring
    request = AWSRequest(method=method.upper(), url=safe_url, data=body)
    SigV4Auth(Session().get_credentials(), "execute-api",
              region).add_auth(request)
    return dict(request.headers.items())


def call(prompt: str, session_id: str):
    body = json.dumps({
        "prompt": prompt,
        "session_id": session_id
    })
    method = "post"
    url = "<your-api-endpoint>"
    r = requests.post(url, headers=signing_headers(method, url, body), data=body)
    response = json.loads(r.text)
    return response