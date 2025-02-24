import logging

#  customs middleware for logging, rate limiting, and authentication

class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)


    def __call__(self, request):
        self.logger.info(f"Request Method: {request.method}, URL:{request.path}")
        response = self.get_response(request)
        return response
    
    