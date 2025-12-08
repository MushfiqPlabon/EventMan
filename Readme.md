# EventMan: Event Management System

## Overview

EventMan is a comprehensive, modern web-based Event Management System built with Django, designed to provide a robust platform for organizing, managing, and participating in various events. This project demonstrates advanced Django features, optimized performance, and a modern frontend with Tailwind CSS and enhanced user experience.

The application empowers administrators with comprehensive user management tools, organizers with efficient event management tools, and provides participants with a user-friendly experience, complete with authentication, role-based access, and RSVP functionality.

## Live Demo

Experience EventMan in action: https://eventman-phi-assign.onrender.com/

> **Note:** It may take a while for the page to load due to it being on free hosting.

## Features

- **User Authentication & Authorization:** Secure user signup, login, and logout with email activation.
- **Email Activation:** Mandatory email verification for new accounts with secure activation links using Django's token generator.
- **Advanced Role-Based Access Control (RBAC):**
  - **Admin:** Full access to all features, including comprehensive user and group management via dedicated admin panel.
  - **Organizer:** Can create, update, and delete events and categories they manage.
  - **Participant:** Can view events and RSVP to them.
- **User-Specific Dashboards:** Intelligent redirection to role-appropriate dashboards (Admin, Organizer, Participant) upon login.
- **Admin User Management:** Dedicated interface for administrators to assign roles to users via Django Groups system.
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
  - **Delete:** Remove events from the system (restricted to organizer or admin) with enhanced SweetAlert2 confirmation dialogs.
- **Category Management (CRUD):** Create, view, update, and delete different categories for events (e.g., "Conference," "Workshop," "Concert").
- **Enhanced RSVP System:**
  - Participants can easily RSVP to events they are interested in.
  - Prevents duplicate RSVPs for the same event via O(1) database checks.
  - Participants can view events they have RSVP'd to on their dedicated dashboard.
  - Enhanced with visual loading states and proper confirmation dialogs.
- **Email Notifications:** Automated email confirmation sent to users upon successful RSVP and account activation.
- **Django Signals:** Utilizes Django's signal framework to automate processes like sending RSVP confirmation emails and account activation emails.
- **Performance Optimized (O(1)/O(log n)):**
  - Database indexes on all frequently queried fields for O(log n) -> O(1) lookups.
  - Cached dashboard statistics and category lists for O(1) access.
  - Optimized queries using select_related and prefetch_related to eliminate N+1 queries.
  - Conditional aggregation for efficient dashboard statistics in single queries.
- **Media File Handling:** Events can have associated images with a default image fallback and client-side validation.
- **Search & Filter:** Easily find events by name, location, or filter by category and date range.
- **Enhanced User Experience:**
  - SweetAlert2 for beautiful confirmation dialogs and notifications.
  - Loading states during form submissions for better feedback.
  - Improved accessibility with proper ARIA labels and semantic HTML.
- **Responsive Design:** User-friendly interface across various devices (mobile, tablet, desktop), powered by Tailwind CSS.
- **Dark Mode (Currently Broken):** Client-side dark mode toggle for improved user experience.

## Technologies Used

- **Backend:** Python, Django
- **Authentication:** `django-allauth`
- **Debugging:** `django-debug-toolbar`
- **Database:** PostgreSQL (production/deployment) - REQUIRED for Render.com deployment, SQLite (local development fallback)
- **Frontend:** HTML, CSS (Tailwind CSS v3.4), JavaScript
- **Frontend Libraries:** SweetAlert2 for enhanced user experience
- **ASGI Server:** Uvicorn for high-performance async web serving
- **Frontend Tooling:** Vite (for fast development and build of Tailwind CSS and JavaScript)
- **Package Management:** Bun for JavaScript dependencies
- **Deployment:** Render.com (PostgreSQL database recommended for persistence)
- **Performance:** Django caching framework for O(1) access to frequent data

## Getting Started

Follow these steps to get EventMan up and running on your local machine:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/MushfiqPlabon/EventMan-Phi-Assign.git
    # Or
    gh repo clone MushfiqPlabon/EventMan-Phi-Assign
    cd EventMan-Phi-Assign
    ```

2.  **Install Python dependencies with uv:**

    ```bash
    uv sync
    ```

    > Ensure `pyproject.toml` includes Django, `django-allauth`, `django-debug-toolbar`, `psycopg2-binary` (for PostgreSQL if used locally), etc.

3.  **Configure Environment Variables:**
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

4.  **Install JavaScript dependencies using bun:**

    ```bash
    bun install
    ```

5.  **Run Vite development server (in a separate terminal):**
    This command watches for changes in your frontend assets and provides hot-reloading. Keep it running during development.

    ```bash
    bun run dev
    ```

6.  **Build static assets for production:**
    This command compiles your Tailwind CSS and JavaScript for production.

    ```bash
    bun run build
    ```

7.  **Apply database migrations:**

    ```bash
    uv run manage.py makemigrations
    uv run manage.py migrate
    ```

8.  **Create default groups:**

    ```bash
    uv run manage.py create_default_groups
    ```

9.  **Create a Django superuser (for admin access):**

    ```bash
    uv run manage.py createsuperuser
    ```

    Follow the prompts to create your admin account. For local testing, you can use:

    - **Username:** `admin`
    - **Password:** `admin123`
      > **Security Warning:** Use a strong, unique password for any production environment.

10. **Run the Django development server:**
    ```bash
    uv run manage.py runserver
    ```
    The application will be accessible at http://127.0.0.1:8000/.

## Running with Uvicorn (ASGI High-Performance Server)

For production-like performance testing or deployment, you can run the application with Uvicorn for better performance:

```bash
uv run uvicorn eventMan.asgi:app --reload
```

Uvicorn provides significant performance improvements through async capabilities, better concurrency, and more efficient resource utilization compared to traditional WSGI servers.

## Testing and Usage

1.  **Access the application:** Open http://127.0.0.1:8000/ in your browser.
2.  **Register a new user:** Use the "Register" link. An activation email will be sent (visible in console if using console backend). Copy the activation link to activate the account.
3.  **Assign roles:** Log in as your superuser (`/admin/`) and assign new users to the `Admin`, `Organizer`, or `Participant` groups.
4.  **Admin Role Management:** Use the `/dashboard/admin/manage-roles/` endpoint to manage user roles via a dedicated interface (only available to admins).
5.  **Explore Dashboards:** Log in with different user roles and verify redirection to their respective dashboards.
6.  **Event/Category Management:** As an Organizer or Admin, create, view, edit, and delete events and categories.
7.  **RSVP to Events:** As a Participant, browse events and use the enhanced RSVP buttons on event detail pages. Check your console for RSVP confirmation emails.
8.  **View RSVP'd Events:** As a Participant, check your dashboard to see events you've RSVP'd to.
9.  **Search and Filter:** Utilize the search bar and filter options on the events list page.
10. **Debugging:** When `DEBUG=True` and your IP is in `INTERNAL_IPS` (e.g., `127.0.0.1`), the `django-debug-toolbar` will be visible on the right side of the page, providing detailed debugging information.

## Project Structure

```
event_management_system/
├── eventMan/                 # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py           # Main Django settings with performance optimizations
│   ├── urls.py               # Project-level URL configurations
│   └── wsgi.py
├── events/                   # Django app for event management
│   ├── management/           # Management commands (create_default_groups)
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py               # Registers signals here
│   ├── decorators.py         # Custom RBAC decorators with caching
│   ├── forms.py              # Event, Category, and Custom Signup forms with client-side validation
│   ├── models.py             # Event, Category models with database indexes
│   ├── signals.py            # Django signals for email notifications
│   ├── urls.py               # App-level URL configurations
│   └── views.py              # Logic for event, category, dashboard, RSVP with caching
├── media/                    # Directory for uploaded media files (e.g., event images)
│   └── event_images/
├── static/                   # Static files (CSS, JS)
│   ├── dist/                 # Compiled CSS/JS from Vite
│   │   ├── main_css.css
│   │   ├── toggle_js.js
│   │   ├── sweetalert_js.js
│   │   └── manifest.json
│   └── src/                  # Source for Tailwind CSS and custom JS
│       ├── input.css         # Tailwind CSS input file
│       └── js/
│           ├── toggle.js     # Dark mode toggle JS
│           └── sweetalert.js # SweetAlert2 functionality
├── templates/                # HTML templates
│   ├── account/              # Django-allauth custom templates
│   ├── dashboards/           # Dashboard specific templates (including role management)
│   ├── emails/               # Email templates for signals
│   └── events/               # Event and Category specific templates with enhanced UX
│   └── base.html             # Base template for all pages
│   └── home.html             # Homepage template
├── .env.example              # Example environment variables file
├── .gitignore
├── db.sqlite3                # SQLite database (for local development)
├── manage.py
├── package.json              # JavaScript dependencies and scripts (using Bun)
├── pyproject.toml            # Python dependencies
└── vite.config.mjs           # Vite configuration for Tailwind CSS
```

## Performance & Optimization

This project implements O(1) and O(log n) time complexity optimizations:

- Database indexes on all frequently queried fields
- Caching for expensive operations (dashboard stats, categories)
- Efficient database queries using select_related, prefetch_related, and conditional aggregations
- Client-side validation and loading states for enhanced UX

## Deployment Notes

This project is configured for deployment on platforms like Render.com. **IMPORTANT**: For deployment on Render.com, you MUST use PostgreSQL as SQLite databases are not persistent on Render's free tier (they get wiped when dynos sleep). Ensure your production environment sets the `DATABASE_URL` environment variable to point to a PostgreSQL database. Other required environment variables include `SECRET_KEY`, `ALLOWED_HOSTS`, `EMAIL_HOST_USER`, and `EMAIL_HOST_PASSWORD` for email functionality.
