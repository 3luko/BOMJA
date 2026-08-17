# BOMJA

**Sound That Brings Us Together.**

BOMJA is an event and community platform built to showcase upcoming events, connect visitors with ticketing platforms, and provide administrators with a simple way to manage event content.

The website is built with Flask, SQLite, HTML, CSS, and JavaScript.

## Features

* Responsive desktop and mobile design
* Dynamic upcoming event listings
* Direct ticket links for events
* Secure administrator login
* Admin dashboard
* Event image uploads
* Event deletion
* Persistent event data using SQLite
* CSRF protection
* Password hashing with bcrypt
* Secure file upload handling
* Responsive event carousel
* Environment-based configuration

## Tech Stack

**Backend**

* Python
* Flask
* SQLite
* Gunicorn

**Frontend**

* HTML
* CSS
* JavaScript
* Jinja2

**Security**

* bcrypt password verification
* Flask-WTF CSRF protection
* Secure Flask sessions
* Restricted file extensions
* Secure filename handling
* Environment variables for credentials and secrets

## Project Structure

```text
BOMJA/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── bomja1.html
│   ├── login.html
│   └── dashboard.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
│
└── data/
    └── bomja.db
```

## Local Development

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory.

```env
SECRET_KEY=your-secret-key
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-bcrypt-password-hash
FLASK_ENV=development
```

Optional local storage paths can also be configured:

```env
DATABASE_PATH=data/bomja.db
UPLOAD_FOLDER=static/uploads
```

> Never commit the `.env` file or production credentials to GitHub.

### 5. Start the development server

```bash
python app.py
```

The development site will normally be available at:

```text
http://127.0.0.1:5000
```

## Database

BOMJA currently uses SQLite.

The application automatically initializes the required database tables when the server starts.

Current tables include:

### `events`

Stores event information including:

* Event ID
* Event image
* Image alt text
* Ticket URL

### `pass`

Stores administrator authentication information including:

* Administrator username
* bcrypt password hash

The application does not store the administrator's plaintext password.

## Event Management

Administrators can log into the dashboard to manage events.

When an event is uploaded:

1. The uploaded file is validated.
2. The filename is sanitized.
3. A unique filename is generated.
4. The image is saved to the configured upload directory.
5. Event information is stored in SQLite.
6. The event automatically appears on the public website.

Events can optionally contain a ticket URL. Events with ticket URLs are clickable and direct visitors to the external ticketing website.

## Security

The application includes several basic production security measures:

* bcrypt password verification
* CSRF protection
* HTTP-only session cookies
* Secure cookies in production
* SameSite cookie protection
* File upload size limits
* Allowed file-extension validation
* Secure filename handling
* UUID-based uploaded filenames
* Parameterized SQLite queries
* Protected administrator routes
* Environment-based secrets

Sensitive information should never be committed to the repository.

The `.gitignore` should include:

```gitignore
.env
.venv/
venv/
__pycache__/
*.pyc
data/*.db
```

## Production

The application is designed to run behind Gunicorn in production.

Example:

```bash
gunicorn app:app
```

Production configuration should provide environment variables for:

```env
SECRET_KEY=
ADMIN_USERNAME=
ADMIN_PASSWORD=
FLASK_ENV=production
DATABASE_PATH=
UPLOAD_FOLDER=
```

The SQLite database and uploaded event images should be stored on persistent storage so they survive application restarts and deployments.

## Updating the Website

Code changes should be developed and tested locally before being pushed to the production branch.

Typical workflow:

```bash
git add .
git commit -m "Describe changes"
git push
```

When automatic deployment is enabled, pushing to the connected production branch triggers a new deployment.

Persistent data such as the SQLite database and uploaded event images should remain separate from application source code and should not be overwritten during deployments.

## Future Development

Planned improvements may include:

* Website analytics
* Event performance analytics
* Ticket click tracking
* Visitor tracking
* Email list integration
* Expanded admin dashboard
* Event editing
* Event scheduling
* Improved content management
* Additional administrator tools

## BOMJA

**Sound That Brings Us Together.**
