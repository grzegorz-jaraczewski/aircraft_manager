class AppError(Exception):
    status_code = 999
    message = "An error occurred."

    def __init__(self, message: str = None):
        if message:
            self.message = message
        super().__init__(f"({self.status_code}) - {self.message}")


class DatabaseIntegrityError(AppError):
    status_code = 500
    message = "Integrity error."


class DatabaseConnectionError(AppError):
    status_code = 503
    message = "Database connection failed."


class InvalidDataError(AppError):
    status_code = 422
    message = "Invalid aircraft data."


class AircraftNotFoundError(AppError):
    status_code = 404
    message = "Aircraft with given 'id' not found."


class AircraftRepositoryError(AppError):
    status_code = 503
    message = "Aircraft repository service is currently unavailable. Please try again later."
