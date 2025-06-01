class DomainError(Exception):
    pass


class CantFindEntityError(DomainError):
    pass


class ValidationError(DomainError):
    pass


class QuotaExceededError(DomainError):
    """Raised when a user exceeds their allocated quota."""

    def __init__(
        self, quota_type: str, current_quota: int, trying_to_add: int, **extra: str
    ) -> None:
        msg = (
            f"Cannot add more items to the user's quota ({quota_type}). "
            f"Current quota: {current_quota}; Trying to add: {trying_to_add}."
        )
        super().__init__(msg)
        self.quota_type = quota_type
        self.current_quota = current_quota
        self.trying_to_add = trying_to_add
        self.extra = extra
