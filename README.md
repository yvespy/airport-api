# ✈️ Airport API
This is a RESTful API for an airport management system built with Django and Django REST Framework. 
It allows you to manage airports, routes, airplane types, airplanes, crew members, flights, and ticket orders.
## Main features
- CRUD operations for:
  - Airports
  - Routes
  - Airplane types
  - Airplanes
  - Crew
  - Flights
  - Orders
- JWT-based authentication
- Full test coverage for all ViewSets
## Project Structure
- `airport_api/` — Django project configuration
- `airport/` — main application with API logic
- `tests/` — test cases for all ViewSets
## Installing using GitHub

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd airport-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   set DB_HOST=<your_db_host>
   set DB_NAME=<your_db_name>
   set DB_USER=<your_db_user>
   set DB_PASSWORD=<your_db_password>
   set DJANGO_SECRET_KEY=<your_secret_key>
   set ACCESS_TOKEN_LIFETIME=<token_lifetime_in_minutes>
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Run the server:
   ```bash
   python manage.py runserver
   ```
## Authentication
- JWT-based authentication is implemented.
- Available endpoints:
  - `/api/token/` — obtain access and refresh tokens
  - `/api/token/refresh/` — refresh the access

