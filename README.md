# Microservices-fastapi-app

This is a python-based web application using FastAPI, following microservices architecture with CI/CD principles. The application provides user authentication and management capabilities and scrapes company dat from openmoney.md.

## Table of Contents

- [Service Overview](#service-overview)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [Authentication FLow](#authentication-flow)
- [Scraping Process](#scraping-process)
- [ELT Process](#elt-process)
- [Development flow steps considering a deployment from AWS](#development-flow-steps-considering-a-deployment-from-aws)
- [TODO/Ideas](#todoideas)

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

![Architecture Diagram](docs/images/architecture_diagram.png)

![Swagger UI](docs/images/swagger_ui.png)

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

Note: Environment files(.env) are included in .gitignore. You need to create them manually based on the templates below.

```
# Gateway service
touch gateway/.env

# App service
touch app_service/.env

# User service
touch user_service/.env

# Scraper service
touch scraper_service/.env
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

1. Registration

```
POST /auth/register/
{
    "username": "testuser",
    "email": "testuser@email.com",
    "password": "password"
}
```

2. Login

```
POST /auth/login/
{
  "username": "user123",
  "password": "securepassword"
}
```

Returns JWT token.

3. Protected Requests Include token in Authorization header:

```
Authorization: Bearer <jwt_token>
```

4. Token Validation

- Tokens are cached in Redis
- Automatic token expiration(30 minutes default)

## Scraping Process

The scraping functionality is accesible through and edpoint that extracts company data from openmoeny.md

1. Request Processing

```
POST /scrape/
{
    "idno": "123456789123"
    "forced_refresh": false
}
```

2. Cache check

Firstly, it checks Redis cache for existing data and then returns cached data immediately if available.

3. Background Scraping

If data is not cached or forced refresh it starts background scraping task.

4. Web Scraping

The service uses Selenium WebDriver with Chrome, navigates to https://openmoney.md/companies/{idno}. It waits for JavaScript content to load into the site(which is a SPA - Single Page Application) and then it extracts complete raw HTML.

## ELT Process

### Extract Phase

The extraction phase uses Selenium WebDriver with Chrome to retrieve raw HTML content from openmoney.md company pages. This approach is necessary because the target website relies on JavaScript to render company information dynamically. The scraper navigates to the specific company URL using the provided IDNO, waits for the page content to fully load including JavaScript-rendered elements, and then captures the complete page source. This ensures that all dynamic content is properly extracted before proceeding to the next phase.

### Load Phase

During the load phase, all extracted raw HTML data is immediately stored in the source_data database table without any processing or transformation. This raw storage approach serves multiple purposes: it creates a complete audit trail of what was scraped and when and enables reprocessing of data without requiring additional web requests. The stored data includes the original URL, complete HTML content, HTTP status code, and timestamp, ensuring full traceability of the scraping operation.

### Transform Phase

The transformation phase processes the raw HTML stored in the database to extract company information. Using BeautifulSoup as the HTML parser, the system analyzes the complete DOM structure to identify and extract relevant data fields. Text processing includes normalization and cleaning operations to ensure data consistency, removing extra whitespace and standardizing formatting. Once the data is successfully parsed and validated, the structured information is stored in the transformed_data table.

## Development flow steps considering a deployment from AWS

1. Code Development & Integration

```
Developer commits code → Push to GitHub repository → CI pipeline triggered
```

When a developer pushes code changes to the main branch or creates a pull request, the automated CI/CD process begins. The GitHub repository serves as the central source of truth, and any code changes immediately trigger the continuous integration workflow.

2. Continuous Integration

```
Code Push → Build Docker image → Security scanning → Vulnerability assessment → Pass/Fail gate
```

The CI workflow automatically:

- Builds the gateway Docker image using the commit SHA as a unique tag
- Runs Trivy security scanner to identify vulnerabilities in OS packages and libraries
- Scans for CRITICAL severity issues that could compromise security
- Fails the pipeline if critical vulnerabilities are detected, preventing unsafe code from progressing

Sensitive data from .env files, such as database passwords and other credentials, will be stored in AWS Secrets Manager and retrieved at build-time during the CD process.

![ci flow diagram](docs/images/ci_flow_diagram.png)

## TODO/Ideas

1. Role-Based Access Control

Implement a role-based access control system that extends beyond the current token-based authentication. This would involve adding a roles table to the user service database, defining three primary roles: admin users who can manage other users and access all system features, standard users who can perform scraping operations and view their own data, and readonly users who can only view cached company information without initiating new scraping requests. The implementation would require modifying the user model to include role assignments, updating the JWT token generation to include role claims, and creating middleware decorators that validate user permissions before allowing access to specific endpoints. Each microservice would need to understand and enforce these role-based permissions, ensuring that sensitive operations like user management and system configuration are restricted to admin users only.

2. AWS Secrets Manager Integration

Transition from local .env files to AWS Secrets Manager for production-grade secret management across all microservices. This implementation would involve creating separate secret stores for each service (user_service/secrets, scraper_service/secrets, etc.) containing database URLs, Redis connection strings, JWT secret keys, and other sensitive configuration data.

3. Expand current GitHub Actions workflow

Expand the current GitHub Actions workflow to include all four microservices with parallel builds, testing, and multi-stage security scanning. The pipeline would build Docker images for app_service, user_service, and scraper_service alongside the existing gateway service. Each service would undergo individual integration testing with temporary database containers, and security vulnerability scanning using tools like Trivy.

4. Scraper Service

Expand the scraper to extract additional company information from openmoney.md beyond just company name and address. This includes implementing parsers for financial data (revenue, profit/loss, assets), registration details (registration date, legal form, authorized capital), contact information (phone numbers, email addresses, website), shareholder information, business activities, etc.
