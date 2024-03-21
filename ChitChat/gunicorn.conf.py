# gunicorn.conf.py

# Bind to the specified IP address and port
bind = '0.0.0.0:8000'

# Number of worker processes
workers = 4

# Worker class for handling ASGI applications (Uvicorn in this case)
worker_class = 'uvicorn.workers.UvicornWorker'

# Timeout for worker processes (in seconds)
timeout = 30

# Maximum number of pending connections
backlog = 2048

# Maximum number of requests a worker will process before restarting
max_requests = 1000

# Maximum jitter to add to the max_requests setting
max_requests_jitter = 50

# Log level (e.g., debug, info, warning, error, critical)
loglevel = 'info'

# Access log file path
accesslog = 'access.log'

# Error log file path
errorlog = 'error.log'
