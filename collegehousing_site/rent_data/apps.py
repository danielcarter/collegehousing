from django.apps import AppConfig

class RentDataConfig(AppConfig):
    name = 'rent_data'

## This is to password protect the site as needed. To turn off the protection, just comment out the appropriate niddleware line in setting.py
import base64

from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse
from django.conf import settings

AUTH_TEMPLATE = """ <html> <title>Authentication Required</title> <body> Authentication required. </body> </html> """

class BasicAuthMiddleware(object):

    def init(self, get_response): self.get_response = get_response

    def _unauthed(self):
        response = HttpResponse(AUTH_TEMPLATE, content_type="text/html")
        response['WWW-Authenticate'] = 'Basic realm="Development"'
        response.status_code = 401
        return response

    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return self._unauthed()
        else:
            authentication = request.META['HTTP_AUTHORIZATION']
            (auth_method, auth) = authentication.split(' ', 1)
            if 'basic' != auth_method.lower():
                return self._unauthed()
            auth = base64.b64decode(auth.strip()).decode('utf-8')
            username, password = auth.split(':', 1)
            if (
                username == settings.BASICAUTH_USERNAME and
                password == settings.BASICAUTH_PASSWORD
            ):
                return self.get_response(request)

            return self._unauthed()
