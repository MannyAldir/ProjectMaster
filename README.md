# Project Master

## What is Project Master
Project Master is a web-based project management application that enables users to organize projects, milestones, and tasks through a centralized dashboard and calendar interface. The application was developed as an academic software engineering project and serves as a prototype for a lightweight project management system. A milestone represents a larger project objective and groups related tasks. Tasks may also exist independently of milestones, allowing users to manage general project to-do items alongside milestone-driven work.

## Features

### Dashboard
- Display active project metrics.
- Summarize upcoming milestone and task deadlines.
- Highlight overdue milestones and tasks
- Calculate project completion progress

### Project Management

- Create, edit, and delete projects.
- Track project status (Active, Inactive, Completed).
- View project progress and associated deliverables.

### Milestone Management

- Create milestones within projects.
- Assign start and end dates.
- Organize project objectives into manageable phases.
- Track milestone completion.

### Task Management

- Create project-level tasks.
- Optionally associate tasks with milestones.
- Assign due dates and priority levels.
- Track task completion status.

### Calendar

- Visualize milestone date ranges.
- Display task due dates as calendar events.
- Color-code events by project.
- View project schedules in a centralized calendar interface.

### Authentication & Authorization

- User registration and login.
- Secure password hashing using Werkzeug.
- Session management with Flask-Login.
- Users can only access and modify their own projects and related data.

### Security

- CSRF protection using Flask-WTF.
- Password hashing and salting.
- User-scoped database queries.
- Server-side input validation.

## Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 Templates
- FullCalendar

### Backend

- Flask
- SQLAlchemy ORM

### Authentication & Security

- Flask-Login
- Flask-WTF
- WTForms
- Werkzeug (Password Hashing)

### Database

- SQLite


## Screenshots

### Login
![Login interface](/documentation/images/login.png)

### Registration
![Registration Page](/documentation/images/register.png)

### Dashboard
![Dashboard Interface](/documentation/images/dashboard.png)

### Project Page
![Project Page](/documentation/images/project_page.png)

### Project detail page
![Project Detail Page](/documentation/images/project_detail.png)

### Calendar Page
![Calendar Page](/documentation/images/calendar_interface.png)

## Getting Started

### Prerequisites

- Python 3.13+
- Git

### Installation

```bash
git clone https://github.com/MannyAldir/ProjectMaster

cd ProjectMaster
```

### Create Virtual Environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

or if you're using uv

```bash
uv sync
```

### Initialize Database

```bash
flask db upgrade
```

### Run the Application

```bash
uv run python app.py
```

or

```bash
python app.py
```

## Limitations
- **No HTTPS protocol**
- **Database stored locally with no backup**
- **No rate limiting**
- **No real-time collaboration**

