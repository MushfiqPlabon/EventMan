# EventMan: Event Management System - Project Context

## MANDATORY GROUND RULES (Highest Priority - Non-Optional)

The following principles are absolutely mandatory and non-optional for all code and documentation in this project and must be enforced by all AI agents:

Library-First Development: Prioritize using established, well-tested libraries before implementing custom solutions to minimize code volume and maximize reliability
Built-in Utilization: Leverage built-in functions and framework features before creating custom implementations
Custom Implementation Restraint: Only create custom code when libraries and built-ins cannot meet specific requirements
DRY (Don't Repeat Yourself): Eliminate all code duplication through reusable functions, components, and modules when it improves customer experience
OOP (Object-Oriented Programming): Utilize OOP principles for code organization and modularity, including encapsulation, inheritance, and polymorphism - ONLY when they enhance customer experience
SOLID Principles: Follow SOLID design principles when they improve customer-facing functionality, but customer experience takes priority
KISS (Keep It Simple, Stupid): Strive for simplicity in design and implementation that benefits the customer, not just the developer
YAGNI (You Aren't Gonna Need It): Avoid over-engineering and unnecessary features - only implement features that directly enhance customer value
Zero Redundancy: Remove all duplicate code, logic, and functionality that doesn't enhance customer experience
Zero Dead Code: Eliminate all unused, unreachable, or commented-out code that doesn't serve customers
Zero Inconsistency: Maintain consistent patterns, naming conventions, and implementation approaches in customer-facing interfaces and experiences
Minimal Code Volume: Keep codebase as small and concise as possible without sacrificing readability while prioritizing customer experience features
Lowest Possible Cyclomatic Complexity: Simplify code logic to reduce complexity while ensuring customer-focused responsiveness
O(1) Time-Complexity: Strive for constant-time operations on critical paths for customer-facing interactions, unless higher complexity is necessary for customer value; otherwise, prefer O(log n) or better
Modularization and Decomposition: Break down large functions and classes into smaller, focused modules to optimize customer experience
Hyper-Efficiency: Optimize for maximum performance and minimal resource usage to enhance customer experience
Customer Experience-First: All technical decisions must serve customer experience first (CUSTOMER IS KING)
User-Centric Design: Focus on delivering a seamless and intuitive user experience. The frontend is the user's reality - design it first, then build the backend to support it.
Zero-Latency: Optimize for sub-50ms perceived customer interaction latency for seamless experience
Scalability & Maintainability: Design systems to handle growth while remaining easy to understand, modify, and extend
Cloud Native Principles: Adhere to cloud-native principles ensuring scalability, resilience, and efficient resource utilization
Extreme Worst-Case Scenario Handling: All implementations must be robust and capable of handling extreme worst scenarios without failure
No Deferred Decisions: All customer-facing decisions must be made upfront
No Loose Ends: Every feature, functionality, and component must be fully implemented and integrated
No Lazy Implementations: All implementations must be thorough and complete
No Temporary Fixes: All fixes and solutions must be permanent and robust
No Procrastination: All tasks and deliverables must be complete without delays
No Half-Measures: All implementations must be comprehensive and fully address customer requirements
Zero-Tolerance for Bugs: All code must be thoroughly checked and verified to be free of bugs before deployment
No Hardcoding: All customer-facing values, configurations, and settings must be dynamic and configurable
Environment Variables: All values come from environment variables (no hardcoded values)
Performance Requirements: Optimize customer-perceived performance over system performance metrics
Validation Strategy: Client validation first for immediate customer feedback, backend validation for security
Error Handling: Graceful degradation with customer-friendly messaging
Mobile-First Design: Optimize for mobile customer interactions as primary use case
Fast Loading: Under 3-second load times for all customer interactions
Customer-First Selection: Use the most efficient technology for customer experience first, regardless of paradigm
State Management: Proper server state and client state with optimistic updates
Required Tools: Use uv and uvx for Python, bun and bunx for JavaScript operations exclusively
No Git Commands: AI agents are strictly prohibited from executing any Git commands

All AI agents working with this codebase must ensure these principles are followed without exception.

## Overview

EventMan is a comprehensive, modern web-based Event Management System built with Django, designed to provide a robust platform for organizing, managing, and participating in various events. This project demonstrates advanced Django features, optimized performance, and a modern frontend with Tailwind CSS and enhanced user experience.

The application empowers administrators with comprehensive user management tools, organizers with efficient event management tools, and provides participants with a user-friendly experience, complete with authentication, role-based access, and RSVP functionality.

## Architecture & Technologies

### Backend
- **Framework**: Django 5.2.4 with Python 3.13
- **Authentication**: `django-allauth` for secure user signup, login, and email verification
- **Database**: PostgreSQL (production) / SQLite (local development) with `dj-database-url` for easy configuration
- **Caching**: Multi-level caching (file-based, locmem, and `django-cachalot` for ORM queries)
- **Performance**: Optimized database queries with indexes, select_related/prefetch_related, and denormalized data for O(1) access to frequently requested data; O(log n) operations for indexed database lookups; O(n) in worst case for full-text search with trigram similarity
- **Background Processing**: Uvicorn ASGI server for high-performance async web serving

### Frontend
- **Framework**: HTML/CSS with Tailwind CSS 3.4 for responsive design
- **Build Tool**: Vite for fast development and build process
- **Libraries**: SweetAlert2 for enhanced user experience
- **Package Manager**: Bun for JavaScript dependencies
- **Static Asset Management**: Vite integration for CSS/JS compilation and asset management

### Key Features
- **Advanced User Management**:
  - Secure user signup/login with email verification
  - Role-based access control (RBAC) with Admin, Organizer, and Participant roles
  - Automatic assignment of Participant role during signup
  - Superuser-based Admin role
  - Organizer role assigned manually via admin panel

- **Event Management**:
  - Full CRUD operations for events and categories
  - Event images with validation and default fallback
  - Date/time validation to prevent past events
  - Search and filtering capabilities

- **Performance Optimizations**:
  - O(1) access to frequently requested data through denormalized models (DashboardStats, participant_count, event_count)
  - O(log n) operations for indexed database lookups (role checks, RSVP status, etc.)
  - O(n) in worst case for full-text search with trigram similarity, though typically performs much better
  - Database indexes on all frequently queried fields
  - Optimized queries using select_related and prefetch_related to avoid N+1 problems
  - Signal-based maintenance of denormalized data for consistent O(1) access

- **RSVP System**:
  - Enhanced RSVP functionality with prevention of duplicate registrations
  - Email notifications upon RSVP
  - Participant count tracking on events

- **User Experience**:
  - Role-specific dashboards with intelligent redirection
  - Responsive design for cross-device compatibility
  - SweetAlert2 for enhanced confirmation dialogs
  - Loading states during form submissions

## Project Structure

```
eventMan/
├── __init__.py
├── asgi.py           # ASGI application configuration
├── context_processors.py  # Context processor for email verification
├── settings.py       # Main Django settings with performance optimizations
├── urls.py           # Project-level URL configurations
├── wsgi.py           # WSGI application configuration
events/               # Django app for event management
├── management/       # Management commands (populate_db)
├── migrations/       # Database migrations
├── services/         # Service layer (currently empty - BloomFilterService removed for database indexing approach)
├── utils/            # Utilities (MessageService)
├── views/            # View modules (main_views, crud_views)
├── __init__.py
├── admin.py          # Django admin configuration
├── apps.py           # App configuration (registers signals)
├── decorators.py     # Custom RBAC decorators with caching
├── forms.py          # Event, Category, and Custom Signup forms
├── models.py         # Event, Category models with database indexes
├── signals.py        # Django signals for email notifications and counters
├── urls.py           # App-level URL configurations
├── user_profile_signals.py  # User profile creation signals
static/               # Static files (CSS, JS)
├── dist/             # Compiled CSS/JS from Vite
│   ├── main_css.css
│   ├── toggle_js.js
│   ├── sweetalert_js.js
│   └── manifest.json
└── src/              # Source for Tailwind CSS and custom JS
    ├── input.css     # Tailwind CSS input file
    └── js/
        ├── toggle.js # Dark mode toggle JS
        └── sweetalert.js # SweetAlert2 functionality
templates/            # HTML templates
├── account/          # Django-allauth custom templates
├── dashboards/       # Dashboard specific templates
├── emails/           # Email templates for signals
└── events/           # Event and Category specific templates
├── base.html         # Base template for all pages
└── home.html         # Homepage template
media/                # Directory for uploaded media files
├── event_images/     # Event-specific images
```

## Default Groups and Role System

The system implements a three-tier role-based access control system:

1. **Admin**: Django superuser accounts (created manually via `createsuperuser` command or with demo data using `populate_db` command)
2. **Organizer**: Users assigned to the "Organizer" group (created automatically when app starts or with demo data using `populate_db` command)
3. **Participant**: Users assigned to the "Participant" group (auto-assigned during signup)

**Important**: The system is designed to be autonomous through multiple approaches:
- The "Participant" group is created automatically when users sign up via the `CustomSignupForm` in `events/forms.py`
- The "Admin" and "Organizer" groups are created automatically when the app starts up via the `apps.py` file
- A complete setup with demo users and data can be achieved using the `populate_db` management command which creates all necessary groups, users with appropriate roles, events, and categories

## Key Performance Optimizations

1. **Database Indexing**:
   - B-tree indexes on frequently queried fields (date, name, location)
   - Multi-column indexes for common query patterns
   - Partial indexes for specific conditions

2. **Caching Strategy**:
   - L1: File-based cache for persistent data
   - L2: LocMem cache for high-frequency access
   - L3: `django-cachalot` for automatic ORM query caching

3. **Denormalized Data**:
   - DashboardStats model for O(1) dashboard access
   - UserProfile model with denormalized counts
   - Event model with participant_count field

4. **Database Indexing**:
   - B-tree indexes for O(log n) exact match lookups on frequently queried fields
   - GIN indexes with trigram similarity for O(n) full-text search in worst case (typically much better)
   - Proper indexing on M2M relationships for O(log n) membership testing
   - Used for optimized RSVP checks
   - Replaced probabilistic Bloom filters with deterministic database indexing

## Development and Deployment

### Local Development Setup
1. Install Python dependencies with `uv sync`
2. Create environment file from `.env.example`
3. Install JavaScript dependencies with `bun install`
4. Run Vite dev server: `bun run dev`
5. Set up database: `uv run manage.py migrate`
6. (Optional) Populate database with demo data: `uv run manage.py populate_db` (creates all groups, users, events, and categories)
7. Create superuser (if not using populate_db): `uv run manage.py createsuperuser`
8. Run server: `uv run manage.py runserver`

### JavaScript Asset Building
- Development: `bun run dev` (watches for changes)
- Production: `bun run build` (compiles and minifies assets)

### ASGI Server
- Production performance: `uv run manage.py runuvicorn --reload` (alternative to default server)

## Important Notes

1. **Group Creation**: The system provides multiple approaches for group creation:
   - Participant group: Created automatically when users sign up
   - Organizer and Admin groups: Created automatically when the app starts via apps.py
   - Complete setup: Use the populate_db management command for a full demo setup with all roles and data

2. **Database Migrations**: Always run migrations after setup to ensure all models and indexes are properly created.

3. **Email Verification**: The system implements email verification with console backend as default for development.

4. **Security**: The application uses Django's built-in security features and includes protection against common vulnerabilities.

5. **Performance**: The system is heavily optimized with database indexing, caching layers, and efficient queries to ensure O(1) or O(log n) access patterns wherever possible.

## Key Files and Modules

- `events/decorators.py`: RBAC decorators with caching for performance
- `events/forms.py`: Custom signup form that auto-assigns Participant role
- `events/models.py`: Data models with performance optimizations and indexes
- `events/signals.py`: Signal handlers for email notifications and counters
- `events/views/`: Separated view modules (main_views, crud_views)
- `eventMan/context_processors.py`: Email verification context processor
- `eventMan/settings.py`: Comprehensive settings with caching and database configuration