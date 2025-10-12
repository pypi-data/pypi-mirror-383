import json
import logging
from collections.abc import Iterable
from http import HTTPStatus

from django.conf import settings
from django.views.generic import View
from django.views.generic.edit import BaseCreateView, BaseUpdateView
from django.views.generic.list import BaseListView

from .response import JsonResponse

logger = logging.getLogger(__name__)


class RestViewMixin(View):
    response_class = JsonResponse
    content_type = 'application/json'
    form_valid_status = HTTPStatus.OK

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if (
            len(kwargs.get('data', {})) == 0
            and self.request.content_type == 'application/json'
            and len(self.request.body)
        ):
            # Check size limit
            max_size = getattr(settings, 'DJREST_MAX_JSON_SIZE', 10485760)  # 10MB default
            if len(self.request.body) > max_size:
                logger.warning(f'JSON request body too large: {len(self.request.body)} bytes')
                raise ValueError('Request body too large')

            kwargs['data'] = json.loads(self.request.body)

        return kwargs

    def serialize(self, obj_or_qs):
        if isinstance(obj_or_qs, Iterable):
            return [self.serialize_one(obj) for obj in obj_or_qs]

        return self.serialize_one(obj_or_qs)

    def serialize_one(self, obj):
        form = self.get_form_for_object(obj)
        serialized = form.initial
        serialized['pk'] = obj.pk
        return serialized

    def get_form_for_object(self, obj, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        kwargs = self.get_form_kwargs()
        kwargs['instance'] = obj

        return form_class(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        context = self.serialize(self.object)
        return self.response_class(context, status=self.form_valid_status)

    def form_invalid(self, form):
        return self.response_class({'errors': form.errors}, status=400)

    def handle_json_error(self, error):
        """Centralized JSON error handling"""
        logger.error(f'JSON error: {str(error)}')
        return self.response_class({'error': f'Invalid JSON: {str(error)}'}, status=400)

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(context, **response_kwargs)


class ListCreateView(RestViewMixin, BaseCreateView, BaseListView):
    form_valid_status = 201

    def get_context_data(self, **kwargs):
        context = BaseListView.get_context_data(self, **kwargs)

        # Serialize the object list
        response_data = {'results': self.serialize(context['object_list'])}

        # Add pagination metadata if pagination is enabled
        if pagination_data := self.get_pagination_metadata(context):
            response_data['pagination'] = pagination_data

        return response_data

    def get_pagination_metadata(self, context):
        """
        Extract pagination metadata from context.

        Override this method to customize pagination metadata format
        or to support custom paginator implementations.

        Args:
            context: Dictionary returned by BaseListView.get_context_data()
                    (includes 'paginator', 'page_obj', 'is_paginated', etc.)

        Returns:
            Dictionary with pagination metadata (count, page, num_pages) or None
        """
        paginator = context.get('paginator')
        page_obj = context.get('page_obj')

        if not (paginator and page_obj):
            return None

        # Build pagination metadata
        metadata = {}

        # Add count if paginator supports it (cursor-based paginators may not have count)
        metadata['count'] = getattr(paginator, 'count', None)

        # Add current page number
        metadata['page'] = getattr(page_obj, 'number', None)

        # Add total number of pages
        metadata['num_pages'] = getattr(paginator, 'num_pages', None)

        return metadata

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except (json.JSONDecodeError, ValueError) as e:
            return self.handle_json_error(str(e))


class UpdateDeleteView(RestViewMixin, BaseUpdateView):
    def get_context_data(self, **kwargs):
        return self.serialize(self.object)

    def post(self, request, *args, **kwargs):
        return self.response_class(status=405)

    def put(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except (json.JSONDecodeError, ValueError) as e:
            return self.handle_json_error(str(e))

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return self.response_class(status=204)
