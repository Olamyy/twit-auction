from flask import jsonify


class Response:

    def __init__(self):
        self._response_ok = []
        self._response_error = []

    @staticmethod
    def response_ok(data):
        response = {'status': 'success', 'data': data}
        return response

    @staticmethod
    def response_error(message,error):
        response = {'status': 'fail', 'message': message, 'error': error}
        return jsonify(response)
