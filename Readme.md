# EventMan: Event Management System

## Overview

**EventMan** is a web-based Event Management System built with Django, designed to provide a comprehensive platform for organizing and managing various events. This project serves as an assignment for **Week 3, Module 9** of Phitron's Software Development Track (SDT)'s Software Development Project (SDP) course.

The application allows organizers to efficiently manage events, categories, and participants, offering a user-friendly interface powered by Tailwind CSS.

## Features

* **Comprehensive Dashboard:** An intuitive homepage for organizers providing a quick overview of key metrics:
    * Total number of events.
    * Total registered participants across all events.
    * Count of past events.
    * Count of upcoming events.
    * A list of events scheduled for the current day.
    * **Interactive Stats:** Clickable statistics on the dashboard that link to filtered event lists (e.g., clicking "Past Events" takes you to a list of past events).

* **Event Management (CRUD):**
    * **Create:** Add new events with details like name, date, time, location, description, and category.
    * **Read:** View a list of all events, and detailed information for each event.
    * **Update:** Modify existing event details.
    * **Delete:** Remove events from the system.

* **Category Management (CRUD):**
    * Manage different categories for events (e.g., "Conference," "Workshop," "Concert").

* **Participant Management (CRUD):**
    * Keep track of participants, including their name and email.
    * Assign participants to events.

* **Optimized Data Retrieval:**
    * Efficient database queries using `select_related` for categories and `prefetch_related` for participants to minimize database hits.
    * Aggregate queries to calculate overall statistics.

* **Advanced Filtering and Search:**
    * Filter events by category.
    * Filter events by a specific date range (start date, end date).
    * Search for events by name or location using case-insensitive matching.

* **Modern UI with Tailwind CSS:**
    * A clean, responsive, and user-friendly interface.
    * Consistent styling across all pages.
    * Integrated dark mode toggle for enhanced user experience.

## Technologies Used

* **Backend:** Python, Django
* **Database:** SQLite (default for development)
* **Frontend:** HTML, CSS (Tailwind CSS), JavaScript
* **Styling Framework:** Tailwind CSS
* **Date/Time Handling:** Django's built-in date/time utilities

## Installation and Setup

Follow these steps to get EventMan up and running on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/MushfiqPlabon/practice-NeonBar.git](https://github.com/MushfiqPlabon/practice-NeonBar.git) # Assuming this is the correct repository for EventMan
    cd EventManagementSystem # Or whatever your project folder is named
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
    pip install -r requirements.txt # Make sure you have a requirements.txt file
    # If not, install individually:
    # pip install Django djangorestframework # Add any other specific libs you used
    ```
    *Note: You may need to create a `requirements.txt` by running `pip freeze > requirements.txt`.*

4.  **Install Tailwind CSS (if not already set up globally or via npm in the project):**
    ```bash
    npm install -D tailwindcss # Ensure Node.js and npm are installed
    npx tailwindcss init
    ```
    *Update `tailwind.config.js` to include paths to your HTML files (e.g., `./templates/**/*.html`, `./events/templates/**/*.html`).*

5.  **Run Tailwind CSS watcher in a separate terminal:**
    ```bash
    npx tailwindcss -i ./events/static/css/input.css -o ./events/static/css/output.css --watch
    ```

6.  **Apply database migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

7.  **Create a superuser (for admin access):**
    ```bash
    python manage.py createsuperuser
    ```
    *Follow the prompts to create your admin username and password.*

8.  **Run the Django development server:**
    ```bash
    python manage.py runserver
    ```

9.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:8000/`. The dashboard should be your homepage. You can access the Django admin panel at `http://127.0.0.1:8000/admin/`.