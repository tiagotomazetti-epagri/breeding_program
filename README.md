# Breeding Program Management System

A robust and scalable web application built with Django to manage a genetic improvement program for apple and pear trees. This system provides a Minimum Viable Product (MVP) for tracking genetic materials, populations, crosses, and phenotypical data, ensuring data integrity and traceability.

## Core Features

*   **Germplasm Active Bank (BAG):** Centralized management of all genetic materials, including Cultivars, Selections (Lineages), and Hybrids.
*   **Automated Code Generation:** The system automatically generates unique internal codes (`C1`, `S5`) and accession codes (`C1xS5A25H1`) to ensure traceability throughout the breeding lifecycle.
*   **Genealogy Tracking:** Detailed tracking of parent-child relationships (Mother/Father) and origin from specific populations or mutations.
*   **Population Management:** Create and manage populations from crosses between two parent materials, with automatic code generation (`C1xS5A25`).
*   **Phenotypical and Phytosanitary Data:** Record crucial data for each genetic material, such as phenology observations (budding, flowering dates) and reactions to diseases.
*   **Logical Deletion:** Genetic materials are never permanently deleted. They are marked as "inactive" to preserve a complete historical record.
*   **Robust Backend Validation:** Business rules are enforced at the model level (`models.py`) to prevent inconsistent data entry, ensuring high data integrity.

## Technology Stack

*   **Backend:** Python 3.x, Django 4.x
*   **Database:** SQLite (for MVP, easily swappable for PostgreSQL or MySQL)
*   **Architecture:** Monolithic (for MVP)

## Project Structure

```
breeding_program/
├── core/                 # Main Django project configuration
│   ├── settings.py
│   └── urls.py
├── germoplasm/           # The core application for the breeding program
│   ├── migrations/
│   ├── templates/
│   ├── init.py
│   ├── admin.py          # Admin interface configuration
│   ├── apps.py
│   ├── models.py         # The heart of the system: data models and business logic
│   ├── services.py       # Business logic functions (e.g., promotions)
│   └── tests.py
├── manage.py             # Django's command-line utility
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

3.  **Install dependencies:**
    (For now, we only need Django, but it's good practice to use a `requirements.txt` file)
    ```bash
    pip install django
    ```

4.  **Apply database migrations:**
    This will create the necessary tables in your SQLite database based on the models defined in `germoplasm/models.py`.
    ```bash
    python manage.py makemigrations germoplasm
    python manage.py migrate
    ```

5.  **Create a superuser:**
    This will allow you to log in to the Django admin panel.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create your username and password.

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

7.  **Access the application:**
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
