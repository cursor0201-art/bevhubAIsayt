import traceback
import json

class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        with open('error_log.json', 'w') as f:
            json.dump({
                'path': request.path,
                'method': request.method,
                'error': str(exception),
                'traceback': traceback.format_exc()
            }, f, indent=4)
        return None
