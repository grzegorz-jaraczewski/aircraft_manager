# Aircraft Manager API

> **Project Status: Archived – No Longer Maintained**  
> This repository is no longer under active development. It is preserved for educational and reference purposes only. No new features, bug fixes, or updates are planned. Contributions and issues may not be reviewed.

---

## Overview

**Aircraft Manager API** is a FastAPI-based backend application designed for managing aircraft data. It provides endpoints for health checks, database initialization, and aircraft-related operations including performance calculations.

Originally built as an educational or experimental project, it demonstrates how to structure a FastAPI application with proper routing, database integration, and dependency management via Poetry.

---

## Features

- **Health Check**: Monitor app and database status.
- **Aircraft Management**: CRUD operations for aircraft data.
- **Performance Calculations**: Compute range and endurance.
- **Database Integration**: Tables are created on app startup.
- **Environment Configurable**: Uses `.env` for runtime settings.

---

## Prerequisites

- Python 3.8+
- PostgreSQL database
- [Poetry](https://python-poetry.org/) for dependency management
- Environment variables defined in a `.env` file

---

## Setup Instructions

### 1. Clone the Repository

```bash
    git clone https://github.com/Greg75/aircraft_manager.git
    cd aircraft_manager
```

### 2. Install Dependencies with Poetry

```bash
    poetry install
```

### 3. Create a `.env` File

```env
    HOST=127.0.0.1
    PORT=8000
    RELOAD=True
    DATABASE_URL=<your-database-url>
```

### 4. Run the Application

```bash
    python main.py
```

The API will be accessible at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## API Endpoints

### Health Check

`GET /health`  
Returns application and database status.

### Aircraft Management

Base path: `/aircrafts`

- `GET /` – Retrieve all aircraft
- `POST /add_aircraft/` – Add a new aircraft
- `PATCH /update_aircraft/{aircraft_id}` – Update aircraft by ID
- `DELETE /delete_aircraft/{aircraft_id}` – Delete aircraft by ID

### Performance Calculations

- `GET /performance/range/{parameters}` – Calculate aircraft range
- `GET /performance/endurance/{parameters}` – Calculate aircraft endurance

---

## Code Overview

| File | Description |
|------|-------------|
| `main.py` | Application entry point |
| `src/utils/init_db.py` | DB table creation logic |
| `src/router/api.py` | API routing logic |
| `src/config/database.py` | Database connection handler |

### Lifespan Events

- **Startup**: Initializes the database
- **Shutdown**: Closes DB connections

---

## Development

Enable FastAPI’s auto-reload for development:

```bash
    uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Testing

Use `pytest` for testing:

```bash
    poetry add pytest --dev
    pytest
```

---

## Deployment

Use Gunicorn for production deployment:

```bash
    gunicorn -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:8000
```

Docker and container orchestration setups are also recommended for production environments.

---

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.

---

## Project Status

**Archived** – This project is not being actively maintained. You are welcome to fork, study, or build upon it, but please note that no support or further development will be provided.
