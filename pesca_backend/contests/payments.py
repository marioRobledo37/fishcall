import mercadopago
from django.conf import settings


sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)


def create_payment_preference(contest, fisher):

    preference_data = {
        "items": [
            {
                "title": f"Inscripción {contest.name}",
                "quantity": 1,
                "unit_price": float(contest.entry_fee),
                "currency_id": "ARS"
            }
        ],
        "payer": {
            "name": fisher.full_name,
        },
        "back_urls": {
            "success": "https://fishcall.app/payment-success",
            "failure": "https://fishcall.app/payment-failure",
            "pending": "https://fishcall.app/payment-pending"
        },
        "auto_return": "approved"
    }

    preference = sdk.preference().create(preference_data)

    return preference["response"]["init_point"]