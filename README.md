# Microservices-fastapi-app

This is a python-based web application using FastAPI, following microservices architecture with CI/CD principles. The application provides user authentication and management capabilities and scrapes company dat from openmoney.md.

## Table of Contents

- [Service Overview](#service-overview)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [Authentication FLow](#authentication-flow)
- [Scraping Process](#scraping-process)
- [ELT Process](#ELT-process)
- [API Documentation](#api-documentation)
- [Development Flow](#development-flow)
- [Testing](#testing)
- [TODO/Ideas](#todo-ideas)

## Service Overview

The application consists of 4 microservices that work together.

### Gateway Service

The Gateway Service acts as the primary entry point for all client
requestsserving as a reverse proxy that routes incoming HTTP requests to the
appropriate backend services. The gateway also manages authentication token
forwarding, ensuring that user credentials are properly transmitted to
services that require authentication. This centralized approach provides a
single point of contact for clients while maintaining clean separation
between the public API and internal service architecture.

### App Service

The App Service functions as the main orchestrator and business logic
handler within the microservices system. It coordinates communication
between the user service and scraper service, acting as a middleware that
processes and validates data flowing between different
components. The service manages workflows that require interaction
with multiple backend services, ensuring that business rules are enforced
consistently across the application.

### User Service

The User Service is used for user management and authentication processes. It handles user registration workflows, including input validation and secure password hashing using b-crypt. The service implements OAuth2.0 token generation and validation. Session management is established through Redis caching, which improves performance by reducing database queries for frequently accessed user data while maintaining session state across multiple requests and services.

### Scraper Service

The Scraper Service specializes in web scraping and data processing operations, specifically designed to extract company information from openmoney.md. It implements ELT (Extract, Load, Transform) pipeline that first extracts raw HTML data from target websites, loads this data into persistent storage for audit and reprocessing capabilities, and then transforms the raw data into structured, usable information.

## Architecture

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.11(for local development)
- PostgreSQL(included in docker-compose)
- Redis(included in docker-compose)

### Environment Setup

1. Clone the repository

```
git clone https://github.com/davidv202/microservices-fastapi-app.git
cd microservices-web-app
```

2. Create enviornment files

```
# Gateway service
cp gateway/.env

# App service
cp app_service/.env

# User service
cp user_service/.env

# Scraper service
cp scraper_service/.env
```

3. Environment Variables

```
# gateway/.env
APP_SERVICE_URL=http://app_service:8001
```

```
# app_service/.env
USER_SERVICE_URL=http://user_service:8002
SCRAPER_SERVICE_URL=http://scraper_service:8003
```

```
# user_service/.env
SECRET_KEY=secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://admin:admin@postgres:5432/user_service_db
REDIS_HOST=redis
REDIS_PORT=6379
```

```
# scraper_service/.env
DATABASE_URL=postgresql://admin:admin@postgres:5432/scraper_service_db
REDIS_HOST=redis
REDIS_PORT=6379
```

### Running with Docker

1. Start all services

```
docker-compose up --build
```

2. Check services status

```
docker-compose ps
```

3. Stop services

```
docker-compose down
```

### Local Development Setup

1. Install dependencies or each service

```
# Gateway
cd ../gateway
pip install -r requirements.txt

# App service
cd ../app_service
pip install -r requirements.txt

# User service
cd user_service
pip install -r requirements.txt

# Scraper service
cd ../scraper_service
pip install -r requirements.txt
```

2. Start services individually

```
# Gateway
cd gateway
uvicorn main:app --host 0.0.0.0 --port 8000

# App Service
cd app_service
uvicorn main:app --host 0.0.0.0 --port 8001

# User Service
cd user_service
uvicorn main:app --host 0.0.0.0 --port 8002

# Scraper Service
cd scraper_service
uvicorn main:app --host 0.0.0.0 --port 8003
```

## Authentication Flow

![Authentication Flow](docs/images/authentication_flow.png)
