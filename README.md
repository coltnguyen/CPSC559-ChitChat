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

Clone the repo:
`git clone https://github.com/coltnguyen/CPSC559-ChitChat.git`

Navigate to ChitChat main directory:
`cd ChitChat`

To install requirements, run:
`pip install -r requirements.txt`

### Step 1: Initialize Redis
`redis-server --bind <insert-ip-here> --protected-mode no`

### Step 2: Initialize Celery Worker

In two separate terminals, run:
`celery -A ChitChat.celery:app worker --loglevel=info`
`celery -A ChitChat.celery:app beat`

(Optional) To activate monitoring:
`celery -A ChitChat.celery:app flower`

### Step 3: Initialize Uvicorn WebSocket
`uvicorn ChitChat.asgi:application --workers=4 --host <insert-ip-here> --port 8000`

## Setup Instructions

1. **Install Dependencies**
   - Python 3.x
   - Django
   - Channels
   - Celery
   - Redis
   - MongoDB

2. **Configure MongoDB**
   - Set up a MongoDB instance or cluster
   - Update the database connection settings in `ChitChat/settings.py`

3. **Configure Redis**
   - Set up a Redis instance
   - Update the Redis connection settings in `ChitChat/settings.py` and `chat/tasks.py`

4. **Run Database Migrations**
   - `python manage.py migrate`

5. **Start the Django Development Server**
   - `python manage.py runserver`

6. **Start Celery Worker**
   - `celery -A ChitChat worker --beat --scheduler django --loglevel=info`

## Key Components

### Models (`chat/models.py`)

- `User`: Represents a user in the system, with fields for first name, last name, username, and password.
- `Message`: Represents a chat message, with fields for user ID, username, chatroom ID, message content, and timestamp.
- `Chatroom`: Represents a chatroom, with a field for the chatroom name.

### Views (`chat/views.py`)

- `chat`: Renders the chatroom HTML template.
- `loginUser`: Handles user login requests.
- `registerUser`: Handles user registration requests.
- `allMessages`: Retrieves all messages for a given chatroom.
- `createMessage`: Creates a new chat message.

### Serializers (`chat/serializers.py`)

- `UserSerializer`: Serializes and deserializes `User` model instances.
- `MessageSerializer`: Serializes and deserializes `Message` model instances.

### Consumers (`chat/consumers.py`)

- `ChatConsumer`: WebSocket consumer that handles real-time chat messaging.

### Tasks (`chat/tasks.py`)

- `run_sync_databases`: Celery task for synchronizing data between the main and replica databases.

### Database Synchronization (`chat/management/commands/sync_databases.py`)

- `Command`: Django management command for synchronizing data between the main and replica databases.

### Database Routing (`chat/routers.py`)

- `ReplicaRouter`: Database router that handles read and write operations for the main and replica databases.

### Templates (`chat/templates/`)

- `chat/chatroom.html`: HTML template for the chatroom page.

### Static Files (`chat/static/`)

- CSS and JavaScript files for styling and client-side functionality.

## Usage

1. Register a new user or log in with an existing account.
2. Join or create a chatroom.
3. Send and receive real-time chat messages within the chatroom.

Note: The application currently does not have any authentication or authorization mechanisms for WebSocket connections, allowing anyone to join and participate in chat rooms.
