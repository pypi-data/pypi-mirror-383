class KubemindError(Exception):
    """Base error for KubeMind."""


class ValidationError(KubemindError):
    pass


class NotFoundError(KubemindError):
    pass


class ConflictError(KubemindError):
    pass


class RateLimitError(KubemindError):
    pass


class AuthError(KubemindError):
    pass


class ExternalServiceError(KubemindError):
    pass


class RetryableError(KubemindError):
    pass

