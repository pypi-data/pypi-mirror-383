from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import JsonResponse as DjJsonResponse


class JsonResponse(DjJsonResponse):
    def __init__(self, data=None, encoder=DjangoJSONEncoder, safe=True, json_dumps_params=None, **kwargs):
        status = kwargs.get('status', 200)

        if data is None:
            if status == 204:
                data = {}
            elif status >= 400:
                # Use HTTP status reason phrase for error responses
                from http import HTTPStatus

                try:
                    reason = HTTPStatus(status).phrase
                    data = {'error': reason}
                except ValueError:
                    data = {'error': 'Unknown error'}
            else:
                data = {}

        super().__init__(data, encoder=encoder, safe=safe, json_dumps_params=json_dumps_params, **kwargs)
