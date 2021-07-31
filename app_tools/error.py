from flask_restful import APIException


class InvalidParameter(APIException):
   status_code = 204
   detail = 'Invalid parameters'