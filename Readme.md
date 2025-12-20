# EventMan: Event Management System

## Overview

EventMan is a comprehensive, modern web-based Event Management System built with Django, designed to provide a robust platform for organizing, managing, and participating in various events. The application empowers administrators with comprehensive user management tools, organizers with efficient event management tools, and provides participants with a user-friendly experience, complete with authentication, role-based access, and RSVP functionality.

## Features

- **User Authentication & Authorization:** Secure user signup, login, and logout with email verification.
- **Role-Based Access Control (RBAC):**
  - **Admin:** Full access to all features, including user and group management.
  - **Organizer:** Can create, update, and delete events and categories.
  - **Participant:** Can view events and RSVP to them.
- **User-Specific Dashboards:** Intelligent redirection to role-appropriate dashboards upon login.
- **Event Management (CRUD):** Create, read, update, and delete events with details like name, date, time, location, description, category, and images.
- **Category Management (CRUD):** Manage different categories for events.
- **Enhanced RSVP System:** Participants can RSVP to events with duplicate prevention and email notifications.
- **Search & Filter:** Find events by name, location, category, and date range.
- **Performance Optimized:** O(1) and O(log n) access to frequently requested data through denormalized models and database indexing.
- **Responsive Design:** User-friendly interface across various devices powered by Tailwind CSS.

## Technologies Used

- **Backend:** Python, Django
- **Authentication:** `django-allauth`
- **Database:** PostgreSQL (production) / SQLite (development)
- **Frontend:** HTML, CSS (Tailwind CSS), JavaScript
- **Frontend Libraries:** SweetAlert2
- **ASGI Server:** Uvicorn
- **Frontend Tooling:** Vite
- **Package Management:** Bun
- **Deployment:** Render.com

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MushfiqPlabon/EventMan-Phi-Assign.git
   cd EventMan-Phi-Assign
   ```

2. **Install Python dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Customize your .env file as needed
   ```

4. **Install JavaScript dependencies:**
   ```bash
   bun install
   ```

5. **Run Vite development server (separate terminal):**
   ```bash
   bun run dev
   ```

6. **Apply database migrations:**
   ```bash
   uv run manage.py makemigrations
   uv run manage.py migrate
   ```

7. **Create a superuser:**
   ```bash
   uv run manage.py createsuperuser
   ```

8. **Run the development server:**
   ```bash
   uv run manage.py runserver
   ```

## Deployment Notes

For deployment on Render.com, PostgreSQL must be used as SQLite databases are not persistent. Ensure your production environment sets the `DATABASE_URL` environment variable to point to a PostgreSQL database.

## Performance & Optimization

This project implements O(1), O(log n), and O(n) time complexity optimizations:
- O(1) access to frequently requested data through denormalized models
- O(log n) operations for indexed database lookups
- Database indexes on all frequently queried fields
- Signal-based maintenance of denormalized data

## Deployment Note

This application has been configured for deployment on Vercel with proper static file handling.