 # Task Management System
 ## Quick Start
 ```bash
 git clone <repo>
 cd task-management-system
 cp .env.sample .env
 docker-compose up

- User management: `/api/users/`
- Task management: `/api/tasks/`

## Frontend

Basic login/logout at `/accounts/login/`, `/accounts/logout/`.

Task list page at `/tasks/`

## Testing

Run tests with: `python manage.py test`