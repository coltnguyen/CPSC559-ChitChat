# gunicorn.conf.py

# Bind to the specified IP address and port
bind = '0.0.0.0:8000'

# Number of worker processes
workers = 4

# Worker class for handling ASGI applications (Uvicorn in this case)
worker_class = 'uvicorn.workers.UvicornWorker'

# Log level (e.g., debug, info, warning, error, critical)
loglevel = 'info'

# Access log file path
accesslog = 'access.log'

# Error log file path
errorlog = 'error.log'
