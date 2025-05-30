# AI Messenger Flask Web Application

A full-stack web application built with Flask that allows users to register, log in, and chat with an AI assistant. This project demonstrates various Flask concepts including user authentication, database interaction with SQLAlchemy, form handling with WTForms, file uploads, and integration with Google's Generative AI (Gemini).

## Features

*   **User Authentication:**
    *   User registration with username, password, and optional avatar upload.
    *   Secure login system with password hashing.
    *   Session management to keep users logged in.
    *   "Remember Me" functionality.
*   **AI Chat Interface:**
    *   Real-time (on page reload) messaging with an AI powered by Google's Generative AI (Gemini model).
    *   Chat history is maintained and sent to the AI for contextual responses.
    *   User and AI messages are visually distinct.
*   **User Profile Management:**
    *   View user profile details including avatar.
    *   Edit profile: update username, password, and avatar.
    *   Delete user account (also deletes associated messages and avatar).
*   **Messaging:**
    *   Users can send messages, which are then responded to by the AI.
    *   Messages are stored in a database.
*   **File Uploads:**
    *   Users can upload profile pictures (avatars) during registration and profile editing.
    *   File type and size validation.
*   **Search:**
    *   Users can search their own message history.
*   **Database:**
    *   SQLite database managed with SQLAlchemy ORM.
    *   User and Message models with relationships.
*   **Structure & Design:**
    *   Object-Oriented Programming principles.
    *   Modular design using Flask Blueprints.
    *   Jinja2 templating for dynamic HTML rendering.
    *   Bootstrap 5 for responsive UI components and basic styling.
    *   Custom CSS for an improved look and feel.

## Technologies Used

*   **Backend:**
    *   Python 3.x
    *   Flask (Web Framework)
    *   Flask-SQLAlchemy (ORM)
    *   Flask-Login (User Session Management)
    *   Flask-WTF (Forms and CSRF Protection)
    *   Werkzeug (Password Hashing, WSGI utilities)
    *   `google-generativeai` (Python SDK for Google AI)
*   **Database:**
    *   SQLite (Default, easily changeable)
*   **Frontend:**
    *   HTML5
    *   CSS3
    *   Bootstrap 5
    *   Jinja2 (Templating Engine)
    *   JavaScript (Basic for UI enhancements like chat scroll)
*   **AI Integration:**
    *   Google AI Studio / Gemini API


## Setup and Installation

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone <your-repository-url>
    cd ai_messenger
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Key and Secret Key:**
    *   Navigate to the `instance/` folder. If it doesn't exist, create it: `mkdir instance`
    *   Create a file named `config.py` inside the `instance/` folder.
    *   Add the following content to `instance/config.py`, replacing placeholders with your actual values:

        ```python
        # instance/config.py
        import os
        from datetime import timedelta

        # Generate one using: python -c "import os; print(os.urandom(24).hex())"
        SECRET_KEY = 'your_actual_strong_random_secret_key_here'

        SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db' # Or your preferred DB URI
        SQLALCHEMY_TRACK_MODIFICATIONS = False

        # Get your Google AI Studio API Key from: https://aistudio.google.com/app/apikey
        GOOGLE_API_KEY = 'YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE'

        PERMANENT_SESSION_LIFETIME = timedelta(days=7)
        MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
        UPLOAD_EXTENSIONS = ['.jpg', '.png', '.jpeg']
        WTF_CSRF_ENABLED = True
        ```
    *   **Note:** The `instance` folder and `config.py` are included in `.gitignore` to keep your secrets out of version control.

5.  **Run the Application:**
    ```bash
    python run.py
    ```
    The application will typically be available at `http://127.0.0.1:5000/`. The first time you run it, the SQLite database (`site.db`) will be created in the `instance/` folder.

## Usage

1.  Navigate to `http://127.0.0.1:5000/` in your web browser.
2.  **Register** a new user account. You can optionally upload a profile picture.
3.  **Login** with your credentials.
4.  You will be redirected to the **Chat** page. Start typing messages to interact with the AI.
5.  Access your **Profile** from the navbar to view details, edit your profile (username, password, avatar), or delete your account.
6.  Use the **Search** bar in the navbar to search through your past messages.
7.  **Logout** when finished.

## Further Development Ideas

*   Real-time messaging using WebSockets (e.g., Flask-SocketIO).
*   More advanced AI context management and conversation memory.
*   Ability to create multiple chat rooms or conversations.
*   User-to-user messaging.
*   Admin panel for user management.
*   Support for different database backends (e.g., PostgreSQL, MySQL).
*   Enhanced UI/UX with a more sophisticated frontend framework or library.
*   More robust error handling and logging.
*   Unit and integration tests.
