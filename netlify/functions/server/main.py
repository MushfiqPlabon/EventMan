import os
import sys
import base64
from io import BytesIO


def handler(event, context):
    """
    Netlify function handler for Django application
    """
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventMan.settings')

    # Add the project directory to Python path
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    sys.path.insert(0, project_dir)

    # Initialize Django
    import django
    django.setup()

    from eventMan.wsgi import app

    # Prepare the WSGI environ dict from the Netlify event
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    body = event.get('body', '') or ''

    # Handle base64 encoded body (Netlify encodes binary data as base64)
    if event.get('isBase64Encoded', False):
        body = base64.b64decode(body)
    elif isinstance(body, str):
        body = body.encode('utf-8')

    # Get query string
    query_string = ""
    if event.get('queryStringParameters'):
        import urllib.parse
        query_string = urllib.parse.urlencode(event['queryStringParameters'])

    # Create the WSGI environ dictionary
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body)),
        'SERVER_NAME': headers.get('host', 'localhost'),
        'SERVER_PORT': '443' if headers.get('x-forwarded-proto') == 'https' else '80',
        'wsgi.url_scheme': headers.get('x-forwarded-proto', 'http'),
        'wsgi.input': BytesIO(body),
        'wsgi.errors': sys.stderr,
        'wsgi.version': (1, 0),
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': True,
    }

    # Add HTTP headers as CGI environ variables
    for header_name, header_value in headers.items():
        if header_name.startswith('HTTP_'):
            environ[header_name.upper()] = str(header_value)
        else:
            environ[f'HTTP_{header_name.upper()}'] = str(header_value)

    # Call the Django WSGI application
    response_parts = {}

    def start_response(status, headers):
        response_parts['status'] = status
        response_parts['headers'] = headers

    # Get the response from Django
    response_iterable = app(environ, start_response)
    body_bytes = b''.join(response_iterable)

    # Parse status code
    status_code = int(response_parts['status'].split()[0])

    # Convert headers to dict
    headers_dict = {h[0]: h[1] for h in response_parts['headers']}

    # Return the response in Netlify's expected format
    return {
        'statusCode': status_code,
        'headers': headers_dict,
        'body': body_bytes.decode('utf-8') if isinstance(body_bytes, bytes) else str(body_bytes),
        'isBase64Encoded': False
    }