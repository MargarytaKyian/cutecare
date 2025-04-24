import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from main.models import Product


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', None)
    if not sig_header:
        return HttpResponse("Missing Stripe Signature", status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse("Invalid signature", status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            client_id = session.get('client_reference_id')
            if not client_id:
                return HttpResponse("Missing client_reference_id", status=400)
            try:
                order = Order.objects.get(id=client_id)
                order.paid = True
                order.stripe_id = session.payment_intent
                order.save()
            except Order.DoesNotExist:
                return HttpResponse("Order not found", status=404)

    # Повертаємо 200 для всіх івентів
    return HttpResponse("Webhook received", status=200)