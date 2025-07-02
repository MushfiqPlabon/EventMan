# EventMan: Event Management System

## Overview

**EventMan** is a web-based Event Management System built with Django, designed to provide a comprehensive platform for organizing and managing various events. This project serves as an assignment for **Week 3, Module 9** of Phitron's Software Development Track (SDT)'s Software Development Project (SDP) course.

The application allows organizers to efficiently manage events, categories, and participants, offering a user-friendly interface powered by Tailwind CSS.

### Live Demo

Experience EventMan in action: [https://eventman-phi-assign.onrender.com/](https://eventman-phi-assign.onrender.com/)
It may take a while for the page to load due to it being on free hosting.

## Features

-   **Comprehensive Dashboard:** An intuitive homepage for organizers providing a quick overview of key metrics:
    -   Total number of events.
    -   Total registered participants across all events.
    -   Count of past events.
    -   Count of upcoming events.
    -   A list of events scheduled for the current day.
    -   **Interactive Stats:** Clickable statistics on the dashboard that link to filtered event lists.

-   **Event Management (CRUD):**
    -   **Create:** Add new events with details like name, date, time, location, description, and category.
    -   **Read:** View a list of all events, and detailed information for each event.
    -   **Update:** Modify existing event details.
    -   **Delete:** Remove events from the system.

-   **Category Management (CRUD):**
    -   Create and manage different categories for events (e.g., "Conference," "Workshop," "Concert").

-   **Participant Management (CRUD):**
    -   Create and manage participant details and their event registrations.

-   **Search & Filter:** Easily find events by name, location, or filter by category and date range.
-   **Responsive Design:** User-friendly interface across various devices, powered by Tailwind CSS.

## Technologies Used

-   **Backend:** Python, Django
-   **Database:** PostgreSQL (production/deployment), SQLite (local development fallback)
-   **Frontend:** HTML, CSS (Tailwind CSS), JavaScript
-   **Deployment:** Render.com

## Getting Started

Follow these steps to get EventMan up and running on your local machine:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/MushfiqPlabon/EventMan-Phi-Assign.git
    #Or
    gh repo clone MushfiqPlabon/EventMan-Phi-Assign
    cd EventMan-Phi-Assign
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables (`.env` file):**
    This project uses environment variables for sensitive data and configuration, allowing it to run seamlessly across different environments (local development, production).
    Create a file named `.env` in the root directory of your project (same level as `manage.py`) and add the following:

    ```
    SECRET_KEY='your_very_secret_key_here' # Replace with a strong, unique key
    DEBUG=True
    DATABASE_URL='sqlite:///db.sqlite3' # For local SQLite, or your PostgreSQL URL for local PG
                                        # Example for PostgreSQL: DATABASE_URL='postgres://user:password@host:port/dbname'
    ALLOWED_HOSTS='127.0.0.1,localhost' # Add your deployment domain here in production (e.g., .onrender.com)
    # CSRF_TRUSTED_ORIGINS='[http://127.0.0.1](http://127.0.0.1),http://localhost' # Add your deployment domain here in production
    ```
    **Note:** The project is configured with conditional logic in `settings.py` to automatically switch between database configurations based on the `DATABASE_URL` environment variable. For local development, if `DATABASE_URL` is not set, it will fall back to SQLite. For deployment on Render, it will use the `DATABASE_URL` provided by the hosting environment.

5.  **Install NPM dependencies and Tailwind CSS:**

    ```bash
    npm install # Ensure Node.js and npm are installed
    npx tailwindcss init
    ```

6.  **Run Tailwind CSS watcher in a separate terminal:**
    This command compiles your Tailwind CSS. Keep it running during development.

    ```bash
    npm run watch:tailwindcss
    ```
7.  **Run Tailwind CSS build incase watcher fails:**
    This command compiles your Tailwind CSS. Keep it running during development.

    ```bash
    npm run build:tailwindcss
    ```

8.  **Apply database migrations:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

9.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

    The application will be accessible at `http://127.0.0.1:8000/`.
