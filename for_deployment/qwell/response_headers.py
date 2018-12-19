"""Exports class: CustomResponse.

This subclass of Response adds Content Security Policy header to responses.
"""

from flask import Response


class CustomResponse(Response):
    def __init__(self, response=None, status=None, headers=None,
                 mimetype=None, content_type=None, direct_passthrough=False):
        if not headers:
            headers = {}
        headers['Content-Security-Policy'] = "style-src 'unsafe-inline' 'self' https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css https://use.fontawesome.com/releases/v5.1.1/css/all.css; img-src 'self' https://storage.googleapis.com/my-project-1542060211099.appspot.com/static/ data:; font-src 'self' https://use.fontawesome.com/releases/v5.1.1/webfonts/;"
        super().__init__(response, status, headers, mimetype, content_type,
                         direct_passthrough)
