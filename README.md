# BOMJA

**Sound That Brings Us Together.**

BOMJA is an event and community platform built to showcase upcoming events, connect visitors with ticketing platforms, and provide administrators with a simple way to manage event content and public-facing media.

The website is built with Flask, SQLite, HTML, CSS, and JavaScript.

## Features

- Responsive desktop and mobile design
- Dynamic upcoming event listings
- Direct ticket links for events and homepage CTAs
- Secure administrator login
- Admin dashboard for managing content
- Event image uploads
- Event deletion and visibility toggling
- Gallery image uploads for past events
- Homepage slideshow management
- Shared ticket destination configuration
- Persistent data using SQLite
- CSRF protection
- Password hashing with bcrypt
- Secure file upload handling
- Responsive event and gallery layouts
- Environment-based configuration

## Tech Stack

### Backend

- Python
- Flask
- SQLite
- Gunicorn

### Frontend

- HTML
- CSS
- JavaScript
- Jinja2

### Security

- bcrypt password verification
- Flask-WTF CSRF protection
- Secure Flask sessions
- Restricted upload file types
- Secure filename handling
- Environment variables for credentials and secrets

## Project Structure

```text
BOMJA/reg-html
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── templates/
│   ├── bomja1.html
│   ├── dashboard.html
│   ├── event_gallery.html
│   ├── login.html
│   └── tickets.html
│
├── static/
│   ├── admin.css
│   ├── bomja-style.css
│   ├── uploads/
│   │   ├── events/
│   │   ├── gallery/
│   │   └── slideshow/
│   ├── visuals/
│   └── js/
│       ├── admin.js
│       └── bomja.js
│
├── data/
│   └── bomja.db
│
└── admin/
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
DATABASE_PATH=data/bomja.db
UPLOAD_FOLDER=static/uploads
```

Optional storage paths can also be customized:

```env
EVENTS_FOLDER=static/uploads/events
GALLERY_FOLDER=static/uploads/gallery
SLIDESHOW_FOLDER=static/uploads/slideshow
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

- Event ID
- Event image filename
- Image alt text
- Event visibility state
- Optional event ticket URL

### `gallery_photos`

Stores gallery media related to past events, including:

- Photo ID
- Linked event ID
- File name
- Alt text
- Upload timestamp

### `slideshow_photos`

Stores homepage slideshow images, including:

- Photo ID
- File name
- Alt text
- Upload timestamp

### `site_settings`

Stores site-wide configuration, including:

- `tickets_url` for homepage and tickets button destinations

### `pass`

Stores administrator authentication information including:

- Administrator username
- bcrypt password hash

The application does not store the administrator's plaintext password.

## Admin Features

Administrators can log into the dashboard to manage site content.

### Event management

When an event is uploaded:

1. The uploaded file is validated.
2. The filename is sanitized.
3. A unique filename is generated.
4. The image is saved to the configured upload directory.
5. Event information is stored in SQLite.
6. The event automatically appears on the public website.

Events can optionally include a ticket URL. Events with ticket URLs are clickable and direct visitors to the external ticketing website.

### Gallery management

Administrators can upload and remove images associated with past events, allowing a structured image gallery for each past event.

### Slideshow management

The admin dashboard includes a slideshow section that allows administrators to upload, preview, and remove homepage slideshow images.

### Shared ticket configuration

The site can use a single saved ticket link that powers the homepage and page-level ticket buttons.

## Security

The application includes several basic production security measures:

- bcrypt password verification
- CSRF protection
- HTTP-only session cookies
- Secure cookies in production
- SameSite cookie protection
- File upload size limits
- Allowed file-extension validation
- Secure filename handling
- UUID-based uploaded filenames
- Parameterized SQLite queries
- Restricted administrator routes
- Environment-based secrets

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

- Website analytics
- Event performance analytics
- Ticket click tracking
- Visitor tracking
- Email list integration
- Expanded admin dashboard
- Event editing
- Event scheduling
- Improved content management
- Additional administrator tools

## BOMJA

**Sound That Brings Us Together.**
