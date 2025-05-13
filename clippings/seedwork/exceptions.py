class DomainError(Exception):
    pass


class CantFindEntityError(DomainError):
    pass


class ValidationError(DomainError):
    pass


class QuotaExceededError(DomainError):
    """Raised when a user exceeds their allocated quota."""
