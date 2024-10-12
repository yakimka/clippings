class DomainError(Exception):
    pass


class CantFindEntityError(DomainError):
    pass


class ValidationError(DomainError):
    pass
