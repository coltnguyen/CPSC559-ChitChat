import socket
import os

class WorkerIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add the worker ID or hostname to the request object
        request.worker_id = self.get_worker_id()
        print(f"request.worker_id={request.worker_id}")
        response = self.get_response(request)
        return response

    def get_worker_id(self):
        # Use either Gunicorn's worker ID or hostname
        return os.environ.get("GUNICORN_WORKER_ID", socket.gethostname())
