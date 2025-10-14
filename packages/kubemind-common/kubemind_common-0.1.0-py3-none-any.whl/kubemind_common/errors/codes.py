class ErrorCode:
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    AUTH_ERROR = "auth_error"
    RATE_LIMITED = "rate_limited"
    EXTERNAL_SERVICE = "external_service_error"
    RETRYABLE = "retryable_error"
    INTERNAL_ERROR = "internal_error"

    @classmethod
    def default_for_status(cls, status: int) -> str:
        if status == 400:
            return cls.VALIDATION_ERROR
        if status == 401 or status == 403:
            return cls.AUTH_ERROR
        if status == 404:
            return cls.NOT_FOUND
        if status == 409:
            return cls.CONFLICT
        if status == 429:
            return cls.RATE_LIMITED
        return cls.INTERNAL_ERROR

