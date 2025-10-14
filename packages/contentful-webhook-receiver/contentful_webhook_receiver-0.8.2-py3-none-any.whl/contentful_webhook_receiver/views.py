# -*- coding: utf-8 -*-
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView

from contentful_webhook_receiver.models import WebhookInvocation
from contentful_webhook_receiver.serializers import WebhookSerializer
from contentful_webhook_receiver.topics import topic_signal_mapping


class WebHookReceiverView(APIView):
    permission_classes = []

    def post(self, request, format=None):
        topic = request.headers.get('X-Contentful-Topic', '')
        serializer = WebhookSerializer(data={'data': request.data, 'type': topic})
        serializer.is_valid(raise_exception=True)
        if getattr(settings, 'LOG_CONTENTFUL_WEBHOOKS', True):
            instance = serializer.save()
        else:
            instance = WebhookInvocation(**serializer.validated_data)
        try:
            signal = topic_signal_mapping[topic]
            signal.send(self.__class__, instance=instance)
        except KeyError as e:
            raise Exception(f'Invalid Contentful topic: {topic}. Could not find a signal for this topic') from e
        return Response()
