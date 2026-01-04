# Notes API with Version History

This project is a RESTful backend service for a note-taking application. It features user authentication, note management, and an automatic version control system that archives previous states of notes upon modification.

**Live Deployment:** https://n-te-xx-1.onrender.com/docs

## Project Overview

The system is built using FastAPI and PostgreSQL. It implements a relational database schema to handle users, notes, and version history. The application is deployed on Render with a cloud-hosted PostgreSQL database on Neon.

### Core Features

* **Authentication:** User registration and login using JWT (JSON Web Tokens) with secure password hashing (bcrypt).
* **Note Management:** Complete CRUD operations (Create, Read, Update, Delete) for notes.
* **Version History:** Automatic archiving of note content. When a note is updated, the previous state is saved to a history table, allowing users to view past versions.
* **Data Validation:** Strict schema validation using Pydantic.
* **Security:** Role-based access control ensuring users can only access their own notes.

## Tech Stack

* **Language:** Python 3.11
* **Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Migration Tool:** Alembic
* **Authentication:** OAuth2 with Password Flow (JWT)
* **Deployment:** Render (Application), Neon (Database)

## Database Schema

The database consists of three primary tables:

1.  **Users:** Stores user credentials and authentication details.
2.  **Notes:** Stores the current state of notes. Contains a foreign key linking to the User.
3.  **NoteVersions:** Stores historical snapshots of notes. Contains a foreign key linking to the Note and the Editor (User).

## Versioning Logic

The version history is implemented using a Copy-on-Write strategy within the `update_note` endpoint:
1.  Before a note is modified, the system fetches the existing data.
2.  This data is inserted into the `NoteVersions` table as a snapshot.
3.  The `Notes` table is then updated with the new content.
4.  Both operations occur within a single atomic database transaction to ensure data integrity.

## Setup Instructions

### Prerequisites
* Python 3.9+
* PostgreSQL (Local or Cloud)

### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Configure Environment Variables:
    Update `app/database.py` with your PostgreSQL connection string or export it as an environment variable:
    ```bash
    export DATABASE_URL="postgresql://user:password@localhost/dbname"
    ```

4.  Run the application:
    ```bash
    uvicorn app.main:app --reload
    ```

5.  Access the API documentation:
    Open `http://127.0.0.1:8000/docs` in your browser.

## API Endpoints Summary

**Authentication**
* `POST /register`: Register a new user.
* `POST /login`: Authenticate and receive an access token.

**Notes**
* `GET /notes/`: Retrieve all notes for the authenticated user.
* `POST /notes/`: Create a new note.
* `PUT /notes/{id}`: Update a note (triggers version snapshot).
* `DELETE /notes/{id}`: Delete a note.

**History**
* `GET /notes/{id}/history`: Retrieve the version history of a specific note.

## Deliverables

* **Source Code:** Hosted in this repository.
* **Postman Collection:** `Notes_API_Project.postman_collection.json` (Included in repository root).
* **Live URL:** https://n-te-xx-1.onrender.com

## Author

**Adwaitha V**
Electronics and Computer Engineering
Amrita Vishwa Vidyapeetham
