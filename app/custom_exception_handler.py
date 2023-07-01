from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['type'] = response.default_code
        response.data["code"] = response.status_code
        response.data["details"] = response.default_detail
        response.data['att'] = str(exc)
    else:
        return Response(exc.msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response
