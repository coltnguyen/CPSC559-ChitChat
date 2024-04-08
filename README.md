# ChitChat

ChitChat is a Django-based web application that provides a real-time chat functionality. It allows users to register, log in, and participate in chat rooms. The application uses WebSockets for real-time communication and MongoDB as the primary database.

## Features

- User registration and authentication
- Real-time chat messaging
- Chat rooms
- Database replication and synchronization

## Project Structure

- `ChitChat/`: The main Django project directory
  - `ChitChat/settings.py`: Project settings
  - `ChitChat/urls.py`: URL routing configuration
  - `ChitChat/asgi.py`: ASGI configuration for WebSocket support
  - `ChitChat/celery.py`: Celery configuration for background tasks
- `chat/`: The main application directory
  - `chat/models.py`: Database models (User, Message, Chatroom)
  - `chat/views.py`: View functions for handling HTTP requests
  - `chat/serializers.py`: Serializers for converting model instances to JSON
  - `chat/consumers.py`: WebSocket consumer for handling real-time chat messages
  - `chat/routing.py`: WebSocket URL routing configuration
  - `chat/tasks.py`: Celery tasks for background jobs (database synchronization)
  - `chat/management/commands/sync_databases.py`: Command for synchronizing databases
  - `chat/routers.py`: Database router for read/write operations
  - `chat/templates/`: HTML templates for rendering views
  - `chat/static/`: Static files (CSS, JavaScript)

## Installation

Navigate to ChitChat main directory and run
`pip install -r requirements.txt`

### Step 1: Initialize Redis
`redis-server --bind <insert-ip-here> --protected-mode no`

### Step 2: Intialize Celery Worker

In two separate terminals, run:
`celery -A ChitChat.celery:app worker --loglevel=info`
`celery -A ChitChat.celery:app beat`

(Optional) To activate monitoring:
`celery -A ChitChat.celery:app flower`

### Step 3: Intialize Uvicorn WebSocket
`uvicorn ChitChat.asgi:application --workers=4 --host <insert-ip-here> --port 8000`
