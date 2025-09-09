###Task Management API Documentation
#Introduction

This is a simple Task Management API built with Django REST Framework.
It helps manage users and tasks (create, read, update, delete).

#How to Run

Make sure you have Docker installed, then run:

docker-compose up


#API will be available at:
👉 http://localhost:8000

#Endpoints
Health

GET /health/ → Check API status

Users

GET /api/v1/users/ → List users

POST /api/v1/users/ → Create user

Tasks

GET /api/v1/tasks/ → List tasks

POST /api/v1/tasks/ → Create task

#Example Request
POST /api/v1/tasks/
Content-Type: application/json

{
  "title": "Write docs",
  "status": "todo",
  "priority": "high"
}

#Tools

You can test the API using:

Swagger

Postman

Insomnia
