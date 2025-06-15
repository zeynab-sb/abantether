# AbanTether Project

## Requirements

- Docker & Docker Compose

## Quick Start

1. **Build and run the project:**
   ```bash
   docker-compose up --build
   ```

2. **The API will be available at:**  
   http://localhost:8000/

3. **Run tests:**
   ```bash
   docker-compose run web python manage.py test
   ```

## Environment Variables

- Database and Redis settings are configured in `docker-compose.yml` and passed to Django via environment variables.

## Useful Endpoints

- **Register:** `POST /api/users/register/`
- **Login:** `POST /api/users/login/`
- **Wallet:** `GET/POST /api/wallet/`, `/api/wallet/deposit/`, `/api/wallet/withdraw/`
- **Orders:** `GET/POST /api/orders/`, `/api/orders/<id>/`

## Notes

- The first time you run, the database will be created and migrations applied automatically.
- You can stop the project with `Ctrl+C` and remove containers with `docker-compose down`.