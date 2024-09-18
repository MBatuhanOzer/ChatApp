# Real-Time Chat Application
This project is a real-time chat application created as a final project for the CS50 Web Programming with Python and JavaScript course. It allows users to engage in live conversations with each other using WebSockets and the ASGI (Asynchronous Server Gateway Interface) framework. This application is a comprehensive demonstration of Django's ability to handle real-time, asynchronous communication.

## Video Description
[ChatApp](https://youtu.be/bkoMdtYegas)

## Features
### User Authentication:

Users can register for an account, log in, and log out securely.
Passwords are hashed using Django's built-in authentication system.
### Real-Time Chat:

Engage in text-based conversations in real-time.
Messages are instantly sent and received without page reloads.
### User Search:

A search bar allows users to find other registered users and initiate a chat.
### Responsive Design:

The application's interface is fully responsive, ensuring usability on both desktop and mobile devices.
## File Descriptions
### models.py
Contains the database models that define the structure of the application's data:

- User Model: Extends Django’s built-in User model to include additional fields specific to the chat application.
- Chat Model: Represents a chat instance between two users.
- Message Model: Stores individual messages, linking each to the appropriate chat and user.
### consumers.py
Defines the WebSocket consumers responsible for handling the real-time communication:

- ChatConsumer: Manages WebSocket connections for individual chat sessions, including sending and receiving messages.
- Redis Cache: Implements Redis caching to efficiently store and retrieve the last 25 messages of a chat, enhancing the user experience.
### views.py
Handles HTTP requests and renders the appropriate templates:

- User Views: Manage user authentication, registration, and profile updates.
- Chat Views: Render chat pages and manage the initiation of new chats.
### urls.py
Maps URL paths to their corresponding view functions:

- Authentication URLs: Include paths for login, logout, and registration.
- Chat URLs: Include paths for accessing and interacting with chat sessions.
### routing.py
Defines the URL routing for WebSocket connections:

- WebSocket URLs: Routes WebSocket connections to the appropriate consumers, ensuring real-time communication for chat sessions.
### asgi.py
Configures ASGI settings for the application:

- ASGI Application: Specifies how Django Channels should handle WebSocket connections.
- Daphne Configuration: Ensures Daphne is correctly set up as the ASGI server.
### settings.py
Contains configuration settings for the entire project:

- Installed Apps: Includes Django Channels, Redis, and other required packages.
- Database Settings: Configures the database connection, ensuring data is stored and retrieved correctly.
- Channel Layers: Defines how Django Channels should interact with Redis for message queuing.
### templates/
A directory containing all HTML templates used in the project:

- Index Template: Contains previous chats and search features.
- Chat Templates: Render the chat interface, dynamically updated through WebSocket communication.
- Authentication Templates: Manage the display of login, registration, and user profile pages.
### static/
Contains static files such as CSS, JavaScript, and images:

- CSS Files: Define the styling for the application, ensuring a consistent and responsive design across devices.
- JavaScript Files: Include custom scripts for handling asynchronous actions, such as sending messages and updating the chat interface in real-time.

### requirements.txt
Lists all Python packages required to run the application, including Django, Django Channels, Daphne, and Redis.

## Caching
The application uses Redis for caching the last 25 messages in each chat, allowing for quick retrieval and display when a user opens a chat. This enhances performance and user experience by reducing the load time for chat history.

- Redis Setup: While Docker is recommended for running Redis, it is not mandatory. If Docker is not used, Redis can be installed and run manually.
## Setup and Installation
1. Clone the repository
   ```bash
   git clone https://github.com/MBatuhanOzer/ChatApp.git
   cd ChatApp
2. Install the required packages
   ```bash
   pip install -r requirements.txt
3. Setup the database
   ```bash
   python3 manage.py makemigrations chat
   python3 manage.py migrate
4. Run redis
   - Using Docker
   ```bash
   docker run -p 6379:6379 -d redis:5
5. Start the Django developement server
   - Standart way
   ```bash
   python3 manage.py runserver
   ```
   - If daphne is not running
   ```bash
   daphne -p 8000 ChatApp.asgi:application
6. Access the application:
   Open a web browser and navigate to http://127.0.0.1:8000/
