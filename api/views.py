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
        root_path = '{}{}'.format(settings.BASE_DIR, '/templates/docs/')
        with open(os.path.join('{}{}'.format(root_path, 'base.json'))) as base_doc_file:
            doc_data = json.load(base_doc_file)

        for file_name in os.listdir(root_path):
            file_ext = file_name.split('.')[1]
            if file_name != 'base.json' and file_ext == 'json':
                with open(os.path.join('{}{}'.format(root_path, file_name))) as doc_file:
                    file_data = json.load(doc_file)
                    for file_data_key, file_data_value in file_data.items():
                        doc_data[file_data_key].update(file_data_value)
        return Response({
            'doc_file': json.dumps(doc_data)
        })


class MultiSerializerViewMixin(object):
    action_serializers = {}

    def get_serializer_class(self):
        if self.action in self.action_serializers:
            return self.action_serializers.get(self.action, None)
        return super().get_serializer_class()
