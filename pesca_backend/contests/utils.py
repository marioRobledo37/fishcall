from pywebpush import webpush
from django.conf import settings
from .models import PushSubscription
import json

def send_push(message):

    subs = PushSubscription.objects.all()

    for s in subs:

        webpush(
            subscription_info=s.subscription,
            data=json.dumps({"message":message}),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"
            }
        )