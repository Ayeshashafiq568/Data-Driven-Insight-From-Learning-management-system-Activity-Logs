import io
import os
import sys
from pathlib import Path

from vercel import Response

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_insights.settings')

import django
django.setup()

from django.core.handlers.wsgi import WSGIHandler

application = WSGIHandler()


def handler(request):
    body = request.body or b''

    scheme = 'https' if request.headers.get('x-forwarded-proto', 'https') == 'https' else 'http'
    host = request.headers.get('host', 'localhost')
    server_name, server_port = (host.split(':', 1) + ['443' if scheme == 'https' else '80'])[:2]
    query_string = request.url.split('?', 1)[1] if '?' in request.url else ''

    environ = {
        'REQUEST_METHOD': request.method,
        'SCRIPT_NAME': '',
        'PATH_INFO': request.path,
        'QUERY_STRING': query_string,
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'SERVER_NAME': server_name,
        'SERVER_PORT': server_port,
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': scheme,
        'wsgi.input': io.BytesIO(body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    for name, value in request.headers.items():
        header_name = name.upper().replace('-', '_')
        if header_name in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            continue
        environ[f'HTTP_{header_name}'] = value

    status_headers = {}

    def start_response(status, headers, exc_info=None):
        status_headers['status'] = status
        status_headers['headers'] = headers

    result = application(environ, start_response)
    response_body = b''.join(result)
    status_code = int(status_headers['status'].split(' ', 1)[0])
    response_headers = {name: value for name, value in status_headers['headers']}
    response_headers['content-length'] = str(len(response_body))

    return Response(response_body, status_code=status_code, headers=response_headers)
