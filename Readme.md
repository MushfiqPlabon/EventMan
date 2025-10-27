# EventMan: A Modern Event Management System

## Project Philosophy: The Intersection of Technology, Business, and Human Connection

> "Man is by nature a social animal." - Aristotle, *Politics*

At its core, EventMan is more than just a software application; it is a tool designed to facilitate human connection. Aristotle's timeless observation reminds us that our need to gather, share experiences, and build communities is fundamental. In the digital age, technology can either isolate or connect us. The philosophical underpinning of EventMan is to be a catalyst for connection, providing a seamless and elegant platform for bringing people together.

From a business perspective, this aligns with the principles of **Experiential Marketing**. In their seminal work, *The Experience Economy*, B. Joseph Pine II and James H. Gilmore argue that businesses must create memorable events and experiences for their customers to build lasting brand loyalty. EventMan is the digital forge for these experiences, providing organizers with the tools to create, manage, and execute events that resonate with their audience and deliver a significant return on investment (ROI).

This document, therefore, is not just a guide to the codebase but a commentary on the choices made, blending computer science principles with marketing and business acumen to create a project that is both technically robust and commercially valuable.

## Live Demo

Experience EventMan in action: [Vercel](https://event-man-drab.vercel.app/)
Backup Deployment: [Render](https://eventman-phi-assign.onrender.com/)

> **Note:** The initial load may be slow as the application is hosted on a free tier, which spins down instances during periods of inactivity.

## Features

### UI/UX Overhaul: Reactive Glass UI

A modern, visually stunning design with comprehensive glassmorphism, transparency, blur, and consistent styling across the entire application.

> ### Developer's Commentary
>
> **BBA/Marketing Principle:** The user interface is the digital "storefront" of the application. A modern, aesthetically pleasing UI directly impacts the perceived value and credibility of the brand. This is explained by the **aesthetic-usability effect**, a phenomenon where users perceive attractive products as more usable. A beautiful UI, as argued by Don Norman in *Emotional Design*, can create a positive emotional response, leading to higher user satisfaction, engagement, and brand loyalty.
>
> **CSE Principle:** The glassmorphism effect, while visually appealing, must be implemented with performance in mind. The use of the CSS `backdrop-filter` property is key here, as it is hardware-accelerated in modern browsers, ensuring a smooth and responsive user experience without overburdening the client's device.

### Real-time Reactivity (HTMX)

Dynamic content updates and seamless microinteractions across the UI, including live statistics on the homepage and real-time updates on all dashboards.

> ### Developer's Commentary
>
> **CSE Principle:** HTMX was chosen over a full-fledged JavaScript framework like React or Vue to maintain the simplicity of a traditional server-rendered architecture while providing a rich, reactive user experience. This approach avoids the complexity of managing a separate frontend application and a stateful client. It embodies the **KISS (Keep It Simple, Stupid)** principle, a design philosophy that favors simplicity in design and implementation. By sending HTML over the wire instead of JSON, we leverage the server's power and keep the client-side logic minimal.
>
> **BBA/Marketing Principle:** The real-time updates provide immediate feedback, which is crucial for a positive user experience. In the context of event management, seeing live stats (e.g., "30 people have RSVP'd!") creates a sense of urgency and **Social Proof**, one of the six key principles of persuasion identified by Robert Cialdini in his book *Influence: The Psychology of Persuasion*. This can significantly increase conversion rates for event sign-ups.

### Payment Gateway Integration (SSLCommerz)

Secure and seamless payment processing for events, including a dedicated checkout page and graceful handling of payment responses.

> ### Developer's Commentary
>
> **CSE Principle:** The payment gateway logic is encapsulated within its own module (`payment_utils.py`), following the **Single Responsibility Principle (SRP)** from the SOLID principles of object-oriented design. This loose coupling makes the system more maintainable and flexible, allowing for the payment provider to be swapped out in the future with minimal impact on the rest of the codebase.
>
> **BBA/Marketing Principle:** A frictionless payment process is critical for maximizing conversions. Any hurdle in the checkout process can lead to "cart abandonment," a major concern in e-commerce. By providing a secure, integrated, and straightforward payment flow, we increase the likelihood of a user completing their ticket purchase, which directly impacts revenue and the financial success of an event.

### Optimized Database Queries

Efficient database interactions using `select_related` and `prefetch_related` for fetching related data, and aggregate queries for statistics.

> ### Developer's Commentary
>
> **CSE Principle:** The use of `select_related` (for `JOIN`ing single-valued relationships) and `prefetch_related` (for `JOIN`ing multi-valued relationships in separate queries) is a deliberate optimization to combat the "N+1 query problem." This ensures that fetching a list of events with their related organizers and participants does not result in a cascade of database queries, which would severely degrade performance. While Donald Knuth famously stated that "premature optimization is the root of all evil," optimizing database access in a web application is rarely premature; it is a fundamental requirement for building a scalable and responsive system.
>
> **BBA/Marketing Principle:** In the digital marketplace, **speed is a feature**. A faster, more responsive application leads to higher user satisfaction and retention. As noted by marketing experts like Philip Kotler, customer satisfaction is a key driver of customer lifetime value (CLV). A slow application frustrates users and can lead them to abandon the platform, directly harming user engagement metrics and the platform's overall success.

---

- **User Authentication & Authorization:** Secure user signup, login, and logout.
- **Email Activation:** Mandatory email verification for new accounts.
- **Role-Based Access Control (RBAC):** Admin, Organizer, and Participant roles with distinct permissions.
- **User-Specific Dashboards:** Tailored dashboards for each user role with real-time data.
- **Event & Category Management (CRUD):** Full create, read, update, and delete functionality for events and categories.
- **RSVP System:** Allows participants to RSVP to events and view their RSVPs.
- **Email Notifications:** Automated email confirmations for RSVPs and account actions.
- **Django Signals:** Automates processes like sending confirmation emails.
- **Media File Handling:** Cloudinary integration for external media storage and delivery via CDN.
- **Search & Filter:** Robust search and filtering capabilities for events.
- **Responsive Design & Dark Mode:** Excellent user experience on all devices with a user-selectable dark mode.

## Technologies Used & Rationale

- **Backend:** Python, Django
  - **Rationale:** Django's "batteries-included" philosophy provides a robust and secure foundation, accelerating development with its built-in ORM, authentication, and admin interface. This allows for a faster **Time-to-Market (TTM)**, a critical business advantage.
- **Database:** PostgreSQL (Production), SQLite (Local)
  - **Rationale:** PostgreSQL is chosen for its robustness, scalability, and reliability in production environments, while SQLite provides a simple, file-based database for easy local development setup.
- **Frontend:** HTML, Tailwind CSS, JavaScript, HTMX
  - **Rationale:** A utility-first CSS framework (Tailwind) combined with the hypermedia-oriented approach of HTMX allows for rapid development of modern, reactive UIs without the overhead of a full single-page application (SPA) framework.
- **Caching & Real-time:** Redis
  - **Rationale:** Redis is an in-memory data store used for caching frequently accessed data. This reduces database load, decreases response times, and improves the overall performance and scalability of the application.
- **Media Storage:** Cloudinary
  - **Rationale:** Offloading media storage to a specialized cloud service like Cloudinary simplifies the application architecture and improves performance by delivering images and other assets via a global Content Delivery Network (CDN).
- **Testing:** `pytest`, `pytest-django`, `factory-boy`, `Faker`
  - **Rationale:** A comprehensive test suite is crucial for ensuring code quality and reliability. As stated by Martin Fowler in *Refactoring*, a solid test suite provides a safety net that enables developers to improve the code's design without fear of breaking existing functionality. From a business perspective, high-quality software builds brand trust and reduces the long-term costs associated with fixing bugs.
- **Dependency Management:** `uv`
  - **Rationale:** `uv` is a modern, extremely fast Python package installer and resolver. Its performance significantly speeds up development and deployment workflows.
- **Deployment:** Render
  - **Rationale:** Render is a modern cloud platform that simplifies the process of deploying web applications, databases, and other services, allowing developers to focus on building features rather than managing infrastructure.

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
    pip install uv # Incase you don't have uv installed already
    uv venv
    # On Windows:
    .\.venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Install Python dependencies:**
    This project uses `uv` for fast and reliable dependency management. Ensure `uv` is installed (e.g., `pip install uv`).

    ```bash
    uv sync
    ```

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
    uv run manage.py makemigrations
    uv run manage.py migrate
    ```

9.  **Create a Django superuser (for admin access):**

    ```bash
    uv run manage.py createsuperuser
    ```

    Follow the prompts to create your admin account.

10. **Create Django Groups for RBAC (via Admin Panel):**

    1.  Run `uv run manage.py runserver`.
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
    uv run manage.py runserver
    ```
    The application will be accessible at http://127.0.0.1:8000/.

## Deployment on Render

This project is configured for deployment on Render. Follow these steps to deploy:

1.  **External Service Setup:**
    *   **Database:** Set up an external PostgreSQL database (e.g., ElephantSQL, Supabase, or a Render PostgreSQL instance) and obtain its connection URL.
    *   **Redis:** Set up an external Redis service (e.g., Upstash Redis or a Render Redis instance) and obtain its URL.
    *   **Cloudinary:** Create a Cloudinary account and obtain your Cloud Name, API Key, and API Secret.
    *   **Email:** Configure an SMTP service for sending emails (e.g., Gmail, SendGrid) and obtain the necessary credentials.

2.  **Render Project Setup:**
    *   Create a new "Web Service" on Render and link it to your Git repository.

3.  **Configure Environment on Render:**
    *   **Environment Variables:** In your Render service settings, go to "Environment" and add all the variables listed in `.env.example` with their actual values from your external services. **Crucially, set `DEBUG` to `False` for production.**
    *   **Build Command:** Set the build command to `./build.sh`. This script will install Node.js dependencies and build the Tailwind CSS assets. Render will automatically install Python dependencies from your `pyproject.toml` file.
    *   **Start Command:** For production, you should use a production-ready web server like Gunicorn. Set the start command to `gunicorn eventMan.wsgi`.
    *   **Database Migrations:** Render can run database migrations on deploy. You can add `python manage.py migrate` as a post-deploy command in the Render dashboard, or add it to your `build.sh` script.

4.  **Deployment:**
    *   Once the service is configured, Render will automatically build and deploy your application on every push to your connected Git branch.

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
