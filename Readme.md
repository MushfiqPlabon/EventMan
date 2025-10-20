# EventMan: Event Management System

## Overview

EventMan is a comprehensive web-based Event Management System built with Django, designed to provide a robust platform for organizing, managing, and participating in various events. This project originally served as an assignment for Week 3, Module 9, updated as a part of Week 4, Module 14, further updated on Week 5, Module 18 (mid-term-exam) of Phitron's Software Development Track (SDT)'s Software Development Project (SDP) course, demonstrating advanced Django features and a modern frontend with Tailwind CSS. But I have changed a lot of stuff around since then.

The application now features a modern, visually stunning "Reactive Glass UI" with comprehensive glassmorphism, real-time reactivity powered by HTMX, and enhanced microinteractions for a truly engaging user experience. It empowers organizers with efficient management tools and provides participants with a user-friendly experience, complete with authentication, role-based access, and RSVP functionality.

## Live Demo

Experience EventMan in action: [https://eventman-phi-assign.onrender.com/]

> **Note:** It may take a while for the page to load due to it being on a free tier hosting.

## Features

- **UI/UX Overhaul: Reactive Glass UI:** A modern, visually stunning design with comprehensive glassmorphism, transparency, blur, and consistent styling across the entire application.
- **Real-time Reactivity (HTMX):** Dynamic content updates and seamless microinteractions across the UI, including live statistics on the homepage and real-time updates on all dashboards (Participant, Organizer, Admin).
- **Enhanced Microinteractions:** Subtle and engaging animations on interactive elements (buttons, cards, links, form inputs) for hover, focus, click, and state changes, powered by `tailwindcss-animate`. This includes a consolidated and enhanced notification system, smooth HTMX content transitions, and improved focus/hover effects for form inputs and interactive elements.
- **Payment Gateway Integration (SSLCommerz):** Secure and seamless payment processing for events, including a dedicated checkout page and graceful handling of payment responses.
- **User Authentication & Authorization:** Secure user signup, login, and logout.
- **Email Activation:** Mandatory email verification for new accounts with secure activation links.
- **Custom Signup Fields:** Includes additional fields like first name and last name during user registration.
- **Role-Based Access Control (RBAC):**
  - **Admin:** Full access to all features, including user and group management.
  - **Organizer:** Can create, update, and delete events and categories they manage.
  - **Participant:** Can view events and RSVP to them.
- **User-Specific Dashboards:** Redirects users to their respective dashboards (Admin, Organizer, Participant) upon login, with real-time updates for key metrics and data.
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
- **Media File Handling:** Events can have associated images with a default image fallback, stored externally via Cloudinary.
- **Optimized Queries:** Efficient database interactions using `select_related` and `prefetch_related` for fetching related data, and aggregate queries for statistics.
- **Search & Filter:** Easily find events by name, location, or filter by category and date range.
- **Responsive Design:** User-friendly interface across various devices (mobile, tablet, desktop), powered by Tailwind CSS.
- **Dark Mode:** Client-side dark mode toggle for improved user experience.

## Technologies Used

- **Backend:** Python, Django, `sslcommerz-lib`
- **Testing:** `pytest`, `pytest-django`, `hammett`, `factory-boy`, `Faker`, `pytest-mock`
- **Authentication:** `django-allauth`
- **Debugging:** `django-debug-toolbar`
- **Database:** Configurable for PostgreSQL (production/deployment), SQLite (local development fallback)
- **Caching & Real-time:** Redis (`django-redis`, `upstash-redis`)
- **Media Storage:** Cloudinary (`django-cloudinary-storage`)
- **Frontend:** HTML, CSS (Tailwind CSS v3), JavaScript, `htmx.org`
- **Frontend Tooling:** Tailwind CSS CLI, PostCSS, Autoprefixer (for compiling CSS), `tailwindcss-animate`
- **Dependency Management:** `uv`
- **Deployment:** Vercel

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
    This project uses `uv` for fast and reliable dependency management. Ensure `uv` is installed (e.g., `pip install uv`).

    ```bash
    uv sync
    ```

    > **Note:** For Vercel deployment, a `requirements.txt` file is generated from `pyproject.toml` and `uv.lock` during the build process.

4.  **Configure Environment Variables:**
    This project uses a `.env` file for environment variables. An example file (`.env.example`) is provided to make setup easier.

    1.  Copy the example file to create your local environment file:
        ```bash
        # On macOS/Linux
        cp .env.example .env
        # On Windows
        copy .env.example .env
        ```
    2.  Open the newly created `.env` file and customize the variables. **It is crucial to fill in all required values for external services (Database, Redis, Cloudinary, Email) if you intend to deploy or use these features locally.** You should also generate a new `SECRET_KEY`.

    > **Security Note:** The `.env` file is ignored by Git (see `.gitignore`) and should never be committed to version control. The project's `settings.py` is configured to automatically switch between configurations based on environment variables. For local development, if `DATABASE_URL` is not set, it will fall back to SQLite. `DEBUG` should be `True` for local development and `False` for production.

5.  **Install NPM dependencies and initialize Tailwind CSS:**
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

    Follow the prompts to create your admin account.

10. **Create Django Groups for RBAC (via Admin Panel):**

    1.  Run `python manage.py runserver`.
    2.  Go to http://127.0.0.1:8000/admin/.
    3.  Log in with your superuser credentials.
    4.  Navigate to "Groups" (under "Authentication and Authorization").
    5.  Add two new groups: `Organizer` and `Participant`.

12. **Run Tests (Optional but Recommended):**
    This project uses `pytest` for comprehensive testing. Ensure your virtual environment is active.

    ```bash
    uv run pytest
    ```

    Test configurations, including global mocks for static files and Cloudinary, are managed in `conftest.py` at the project root.

13. **Run the Django development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be accessible at http://127.0.0.1:8000/.

## Deployment on Vercel

This project is configured for serverless deployment on Vercel. Follow these steps to deploy:

1.  **External Service Setup:**
    *   **Database:** Set up an external PostgreSQL database (e.g., ElephantSQL, Supabase, Render PostgreSQL) and obtain its connection URL.
    *   **Redis:** Set up an external Redis service (e.g., Upstash Redis, Redis Cloud) and obtain its URL and token.
    *   **Cloudinary:** Create a Cloudinary account and obtain your Cloud Name, API Key, and API Secret.
    *   **Email:** Configure an SMTP service for sending emails (e.g., Gmail, SendGrid) and obtain the necessary credentials.

2.  **Vercel Project Setup:**
    *   Create a new project on Vercel and link it to your Git repository.

3.  **Configure Environment Variables on Vercel:**
    *   In your Vercel project settings, go to "Environment Variables" and add all the variables listed in `.env.example` with their actual values from your external services. **Crucially, set `DEBUG` to `False` for production.**

4.  **Build Configuration:**
    *   The project includes `vercel.json` and `build.sh` which are pre-configured for Vercel deployment.
    *   `vercel.json` defines the Python runtime (`python3.12`), handles static file serving, and routes requests to your Django WSGI application.
    *   `build.sh` automates the installation of Python dependencies (using `pip install -r requirements.txt` from a `uv`-generated file), Node.js dependencies, Tailwind CSS build, static file collection, and database migrations.

5.  **Deployment:**
    *   Once environment variables are set and the project is linked, Vercel will automatically build and deploy your application on every push to your connected Git branch.

## Testing and Usage 🧪

### Comprehensive Test Suite
This project features a robust and comprehensive backend test suite built with `pytest` and `hammett`. It leverages `factory-boy` and `Faker` for efficient and dynamic test data generation, ensuring thorough coverage of core functionalities.

**Key aspects of the test suite:**
*   **Frameworks:** `pytest`, `pytest-django`, `hammett`, `factory-boy`, `Faker`, `pytest-mock`.
*   **Coverage:** Dedicated test files for:
    *   Models (`events/tests/test_models.py`)
    *   Views (`events/tests/test_views.py`)
    *   Forms (`events/tests/test_forms.py`)
    *   Signals (`events/tests/test_signals.py`)
    *   Management Commands (`events/tests/test_management_commands.py`)
    *   Payment Gateway Integration (`events/tests/test_payments.py`)
    *   Dashboards (`events/tests/test_dashboards.py`)
*   **Dynamic Data:** Utilizes `factory-boy` and `Faker` to create realistic and varied test data on-the-fly, reducing boilerplate and improving test maintainability.
*   **Mocks:** Employs `pytest-mock` for effective mocking of external dependencies (e.g., Cloudinary uploads, SSLCommerz API calls, static file lookups) to ensure fast and isolated tests.
*   **Global Fixtures:** Common test setup (like global mocks) is managed in `conftest.py` at the project root.

To run the tests, ensure your virtual environment is active and execute:
```bash
uv run pytest
```

### Populating Demo Data

To quickly set up your database with sample users, categories, and events for testing and demonstration purposes, **especially to experience the new UI/UX and real-time features**, use the `populate_demo_data` management command.

```bash
python manage.py populate_demo_data
```

This command will create:
*   **Admin User:** `username=admin`, `password=admin123`
*   **Organizer User:** `username=organizer`, `password=organizer123`
*   **Participant User:** `username=participant`, `password=participant123`

It will also create sample categories and events, including upcoming, past, and draft events. If these users or data already exist, the command will skip their creation.

---

1.  **Access the application:** Open http://127.0.0.1:8000/ in your browser.
2.  **Register a new user:** Use the "Register" link. An activation email will be printed to your Django server console. Copy the activation link from the console and paste it into your browser to activate the account.
3.  **Assign roles:** Log in as your superuser (`/admin/`) and assign new users to the `Organizer` or `Participant` groups.
4.  **Explore Dashboards:** Log in with different user roles and verify redirection to their respective dashboards.
5.  **Event/Category Management:** As an Organizer or Admin, create, view, edit, and delete events and categories.
6.  **RSVP to Events:** As a Participant, browse events and use the "RSVP" button on event detail pages. Check your Django server console for RSVP confirmation emails.
7.  **View RSVP'd Events:** As a Participant, check your dashboard to see events you've RSVP'd to.
8.  **Search and Filter:** Utilize the search bar and filter options on the events list page.
9.  **Debugging:** When `DEBUG=True` and your IP is in `INTERNAL_IPS` (e.g., `127.0.0.1`), the `django-debug-toolbar` will be visible on the right side of the page, providing detailed debugging information.
