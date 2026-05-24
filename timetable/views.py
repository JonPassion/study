import json
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .conversation import handle_message

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_webhook(request):
    """
    Meta WhatsApp Cloud API webhook.
    GET  — verification challenge
    POST — incoming messages
    """
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        verify_token = settings.WEBHOOK_VERIFY_TOKEN
        if mode == 'subscribe' and token == verify_token:
            logger.info("Webhook verified successfully.")
            return HttpResponse(challenge, content_type='text/plain')
        else:
            logger.warning(f"Webhook verification failed. mode={mode}, token={token}")
            return HttpResponse("Forbidden", status=403)

    # POST — process incoming message
    try:
        body = json.loads(request.body)
        logger.debug(f"Webhook payload: {json.dumps(body)}")
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Failed to parse webhook body: {e}")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    try:
        entry = body.get('entry', [])
        for e in entry:
            changes = e.get('changes', [])
            for change in changes:
                value = change.get('value', {})
                messages = value.get('messages', [])
                for msg in messages:
                    if msg.get('type') == 'text':
                        from_number = msg['from']
                        text = msg['text']['body']
                        logger.info(f"Incoming from {from_number}: {text}")
                        handle_message(from_number, text)
    except Exception as ex:
        logger.exception(f"Error processing webhook message: {ex}")

    return JsonResponse({'status': 'ok'})
