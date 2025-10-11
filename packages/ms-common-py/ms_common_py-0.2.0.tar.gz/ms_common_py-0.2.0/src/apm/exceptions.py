from .const import DEFAULT_SERVICE_NAME, ResponseMessageList


class ServiceException(Exception):
    def __init__(self, status=ResponseMessageList.ERROR, code=500, message='Internal Server Error', kind=None,
                 service=DEFAULT_SERVICE_NAME):
        self.status = status
        self.code = code
        self.kind = kind or self.__class__.__name__
        self.service = service
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


class AuthenticationFailure(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=401, message='Authentication Failed',
                 kind='AuthenticationFailure', service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class ForbiddenException(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=403, message='Forbidden', kind='ForbiddenException',
                 service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class BadRequestException(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=403, message='BadRequest', kind='BadRequestException',
                 service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class MissingParamException(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=406, message='MissingParam error',
                 kind='MissingParamException', service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class InternalServerError(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=500, message='Internal Server Error',
                 kind='InternalServerError', service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class ValidateException(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=422, message='Validate Exception',
                 kind='ValidateException', service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class ProductClosedException(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=450, message='Product Closed Exception',
                 kind='ProductClosedException', service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class BusinessException(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=422, message='Business Exception',
                 kind='BusinessException', service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class RequestFailure(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=400, message='Request Failure.', kind='RequestFailure',
                 service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class NotFoundException(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=404, message='Not Found Exception',
                 kind='NotFoundException', service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class HTTPMethodException(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=500, message='Invalid HTTP method',
                 kind='HTTPMethodException', service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)


class BillNotValidException(ServiceException):
    def __init__(self, status=ResponseMessageList.ERROR, code=451, message='Bill Not Valid',
                 kind='BillNotValidException', service=DEFAULT_SERVICE_NAME):
        super().__init__(status=status, code=code, message=message, kind=kind, service=service)
