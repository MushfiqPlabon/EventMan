# EventMan: Event Management System

## Overview

EventMan is a comprehensive web-based Event Management System built with Django, designed to provide a robust platform for organizing, managing, and participating in various events. This project serves as an assignment for Week 3, Module 9, updated as a part of Week 4, Module 14, further updated on Week 5, Module 18 (mid-term-exam) of Phitron's Software Development Track (SDT)'s Software Development Project (SDP) course, demonstrating advanced Django features and a modern frontend with Tailwind CSS.

The application empowers organizers with efficient management tools and provides participants with a user-friendly experience, complete with authentication, role-based access, and RSVP functionality.

## Live Demo

Experience EventMan in action: https://eventman-phi-assign.onrender.com/

> **Note:** It may take a while for the page to load due to it being on free hosting.

## Features

- **User Authentication & Authorization:** Secure user signup, login, and logout.
- **Email Activation:** Mandatory email verification for new accounts with secure activation links.
- **Custom Signup Fields:** Includes additional fields like first name and last name during user registration.
- **Role-Based Access Control (RBAC):**
  - **Admin:** Full access to all features, including user and group management.
  - **Organizer:** Can create, update, and delete events and categories they manage.
  - **Participant:** Can view events and RSVP to them.
- **User-Specific Dashboards:** Redirects users to their respective dashboards (Admin, Organizer, Participant) upon login.
- **Comprehensive Dashboard:** An intuitive homepage for organizers providing a quick overview of key metrics:
  - Total number of events.
  - Total registered participants across all events.
  - Count of past events.
  - Count of upcoming events.
  - A list of events scheduled for the current day.
- **Interactive Stats:** Clickable statistics on the dashboard that link to filtered event lists.
- **Event Management (CRUD):**
  - **Create:** Add new events with details like name, date, time, location, description, category, and an associated image.
  - **Read:** View a list of all events, and detailed information for each event, including participants.
  - **Update:** Modify existing event details (restricted to organizer or admin).
  - **Delete:** Remove events from the system (restricted to organizer or admin).
- **Category Management (CRUD):** Create, view, update, and delete different categories for events (e.g., "Conference," "Workshop," "Concert").
- **RSVP System:**
  - Participants can easily RSVP to events they are interested in.
  - Prevents duplicate RSVPs for the same event.
  - Participants can view events they have RSVP'd to on their dedicated dashboard.
- **Email Notifications:** Automated email confirmation sent to users upon successful RSVP.
- **Django Signals:** Utilizes Django's signal framework to automate processes like sending RSVP confirmation emails and account activation emails.
- **Media File Handling:** Events can have associated images with a default image fallback.
- **Optimized Queries:** Efficient database interactions using `select_related` and `prefetch_related` for fetching related data, and aggregate queries for statistics.
- **Search & Filter:** Easily find events by name, location, or filter by category and date range.
- **Responsive Design:** User-friendly interface across various devices (mobile, tablet, desktop), powered by Tailwind CSS.
- **Dark Mode:** Client-side dark mode toggle for improved user experience.

## Technologies Used

- **Backend:** Python, Django
- **Authentication:** `django-allauth`
- **Debugging:** `django-debug-toolbar`
- **Database:** PostgreSQL (production/deployment), SQLite (local development fallback)
- **Frontend:** HTML, CSS (Tailwind CSS v3), JavaScript
- **Frontend Tooling:** Tailwind CSS CLI, PostCSS, Autoprefixer (for compiling CSS)
- **Deployment:** Render.com

## Getting Started

Follow these steps to get EventMan up and running on your local machine:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/MushfiqPlabon/EventMan-Phi-Assign.git
    # Or
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

3.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    > Ensure `requirements.txt` includes Django, `django-allauth`, `django-debug-toolbar`, `psycopg2-binary` (for PostgreSQL if used locally), etc.

4.  **Configure Environment Variables:**
    This project uses a `.env` file for environment variables. An example file is provided to make setup easier.

    1.  Copy the example file to create your local environment file:
        ```bash
        # On macOS/Linux
        cp .env.example .env
        # On Windows
        copy .env.example .env
        ```
    2.  Open the newly created `.env` file and customize the variables. For local development, the defaults are likely sufficient, but you should generate a new `SECRET_KEY`.

    > **Note:** The `.env` file is ignored by Git (see `.gitignore`) and should never be committed to version control. The project is configured with conditional logic in `settings.py` to automatically switch between database configurations based on the `DATABASE_URL` environment variable. For local development, if `DATABASE_URL` is not set, it will fall back to SQLite. For deployment on Render, it will use the `DATABASE_URL` provided by the hosting environment. The `INTERNAL_IPS` variable is used by `django-debug-toolbar` to determine whether to show the toolbar.

5.  **Install NPM dependencies and initialize Tailwind CSS with Vite:**
    The project includes `package.json`, so you just need to install the dependencies.

    ```bash
    npm install
    ```

6.  **Run Tailwind CSS development server (in a separate terminal):**
    This command watches for changes in your frontend assets and provides hot-reloading. Keep it running during development.

    ```bash
    npm run dev
    ```

7.  **Run Tailwind CSS build (for production deployment or initial setup):**
    This command compiles your Tailwind CSS for production.

    ```bash
    npm run build
    ```

8.  **Apply database migrations:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

9.  **Create a Django superuser (for admin access):**

    ```bash
    python manage.py createsuperuser
    ```

    Follow the prompts to create your admin account. For local testing, you can use:

    - **Username:** `admin`
    - **Password:** `admin123`
      > **Security Warning:** Use a strong, unique password for any production environment.

10. **Create Django Groups for RBAC (via Admin Panel):**

    1.  Run `python manage.py runserver`.
    2.  Go to http://127.0.0.1:8000/admin/.
    3.  Log in with your superuser credentials.
    4.  Navigate to "Groups" (under "Authentication and Authorization").
    5.  Add two new groups: `Organizer` and `Participant`.

11. **Run the Django development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be accessible at http://127.0.0.1:8000/.

## Testing and Usage 🧪

1.  **Access the application:** Open http://127.0.0.1:8000/ in your browser.
2.  **Register a new user:** Use the "Register" link. An activation email will be printed to your Django server console. Copy the activation link from the console and paste it into your browser to activate the account.
3.  **Assign roles:** Log in as your superuser (`/admin/`) and assign new users to the `Organizer` or `Participant` groups.
4.  **Explore Dashboards:** Log in with different user roles and verify redirection to their respective dashboards.
5.  **Event/Category Management:** As an Organizer or Admin, create, view, edit, and delete events and categories.
6.  **RSVP to Events:** As a Participant, browse events and use the "RSVP" button on event detail pages. Check your Django server console for RSVP confirmation emails.
7.  **View RSVP'd Events:** As a Participant, check your dashboard to see events you've RSVP'd to.
8.  **Search and Filter:** Utilize the search bar and filter options on the events list page.
9.  **Debugging:** When `DEBUG=True` and your IP is in `INTERNAL_IPS` (e.g., `127.0.0.1`), the `django-debug-toolbar` will be visible on the right side of the page, providing detailed debugging information.

## Deployment Notes

This project is configured for deployment on platforms like Render.com. Ensure your production environment variables (e.g., `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS`) are correctly set.
