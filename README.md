# Breeding Program Management System

A robust and scalable web application built with Django to manage a genetic improvement program for apple and pear trees. This system provides a solid foundation for tracking genetic materials, populations, crosses, and phenotypical data, ensuring data integrity and traceability.

## Core Features

*   **Germplasm Active Bank (BAG):** Centralized management of all genetic materials, including Cultivars, Selections, and Hybrids.
*   **Automated Code Generation:** The system automatically generates unique internal codes (`C1`, `S5`) and accession codes (`C1xS5A25H1`) to ensure traceability throughout the breeding lifecycle.
*   **Advanced Genealogy Tracking:** Detailed tracking of parent-child relationships (Mother/Father), origin from specific populations, or as mutations of existing cultivars.
*   **Robust Backend Validation:** Business rules are enforced at the model level (`models.py`) to prevent inconsistent data entry (e.g., a material cannot have both a population and manual parents), ensuring high data integrity.
*   **Multiple Photo Uploads:** Associate multiple photos with each genetic material, with automatic and secure file renaming to prevent conflicts.
*   **Dynamic Admin Filters:** The admin interface includes dynamic filters, such as a filter for `Population` by `Seplan Code`, which is populated based on existing data.
*   **Logical Deletion:** Genetic materials are never permanently deleted. They are marked as "inactive" to preserve a complete historical record.

## Technology Stack

*   **Backend:** Python 3.x, Django 4.x
*   **Database:** SQLite (for MVP, easily swappable for PostgreSQL or MySQL)
*   **Image Processing:** Pillow

## Project Structure

```
breeding_program/
├── core/                 # Main Django project configuration
│   ├── settings.py
│   └── urls.py
├── germoplasm/           # The core application for the breeding program
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── admin.py          # Admin interface configuration and custom filters
│   ├── models.py         # The heart of the system: data models and business logic
│   └── ...
├── media/                # (In .gitignore) User-uploaded files (e.g., photos)
├── manage.py             # Django's command-line utility
├── Dockerfile            # (Optional) For containerized development
├── docker-compose.yml    # (Optional) For containerized development
├── requirements.txt      # Project dependencies
└── README.md             # This file
```


## Getting Started

Follow these instructions to get a local copy of the project up and running for development and testing purposes.

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)
*   `venv` (recommended for virtual environments)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tiagotomazetti-epagri/breeding_program.git
    cd breeding_program
    ```

2.  **Create and activate a virtual environment:**
    *   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Configure Environment Variables:**
    This project uses an `.env` file to manage secret keys.
    ```bash
    # Copy the example file to create your local environment file
    cp .env.example .env
    ```
    Now, open the `.env` file and replace `your_secret_key_goes_here` with a real Django secret key. You can generate a new key using an online generator or a Python script.


4.  **Install dependencies from `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Media URLs in `core/urls.py`:**
    Add the following to the end of your main `urls.py` file to serve media files in development:
    ```python
    from django.conf import settings
    from django.conf.urls.static import static

    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    ```

6.  **Apply database migrations:**
    This will create the necessary tables in your database.
    ```bash
    python manage.py makemigrations germoplasm
    python manage.py migrate
    ```

7.  **Create a superuser:**
    This will allow you to log in to the Django admin panel.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create your username and password.

8.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

9.  **Access the application:**
    *   Open your web browser and navigate to `http://127.0.0.1:8000/admin/`.
    *   Log in with the superuser credentials you created.
    *   You can now start managing your germplasm data!

## Business Logic Overview

The system is built around a set of core business rules enforced by the backend:

1.  **Genealogy Integrity:** A genetic material can originate from:
    *   A **Population** (for program-generated hybrids ).
    *   **Manual Parents** (for external materials).
    *   A **Mutation** of an existing material.
    The system strictly forbids combining these origins for a single material, ensuring data consistency.

2.  **Automatic Status:** A material is automatically considered "from the program" (`is_epagri_material = True`) if it is linked to a population.

3.  **Promotion Lifecycle:**
    *   A `HYBRID` can be promoted to a `SELECTION`.
    *   A `SELECTION` can be promoted to a `CULTIVAR`.
    *   During promotion, the material retains its original codes for full traceability while gaining a new, sequential internal code for its new status.

---
