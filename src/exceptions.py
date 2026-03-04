class ServiceException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

class DeploymentException(ServiceException):
    def __init__(self, message: str) -> None:
        super().__init__(message)

