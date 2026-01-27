class DatabaseError(Exception):
    """Raised when there's a database operation error"""
    pass

class DatabaseConnectionError(Exception):
    """Raised when there's a database connection error"""
    pass

class NotFoundError(Exception):
    """Raised when a resource is not found"""
    pass

class ValidationError(Exception):
    """Raised when data validation fails"""
    pass

class ConflictError(Exception):
    """Raised when there's a conflict, like duplicate entry"""
    pass