import os
import json

from django.conf import settings

from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.views import APIView


class APIDocView(APIView):
    template_name = 'docs/index.html'
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request, *args, **kwargs):
        with open(os.path.join(settings.BASE_DIR, 'templates/docs/doc.json')) as doc_file:
            return Response({
                'doc_file': json.dumps(json.load(doc_file))
            })


class MultiSerializerViewMixin(object):
    action_serializers = {}

    def get_serializer_class(self):
        if self.action in self.action_serializers:
            return self.action_serializers.get(self.action, None)
        return super().get_serializer_class()
