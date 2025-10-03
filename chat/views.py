import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import requests
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


logger = logging.getLogger(__name__)

@csrf_exempt
def chatbot(request):
    

    if request.method == "GET":
        return render(request, "chat.html")
    

    try:
        body= json.loads(request.body.decode('utf-8')) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    user_message = body.get("message","").strip()

    if not user_message:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    api_key = getattr(settings, 'OPENROUTER_API_KEY', None)

    if not api_key:
        logger.error("OpenRouter API key is not configured.")
        return JsonResponse({'error': 'Server configuration error'}, status=500)
    
    try:
        resp = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [{"role": "user", "content": user_message}],

            },
            timeout=15,
        )

    except requests.RequestException as exc:
        logger.exception("Error communicating with OpenAI API: %s", exc)
        return JsonResponse({'error': 'Error communicating with AI service'}, status=502)

    if resp.status_code != 200:
        logger.error("OpenAI API error %s: %s", resp.status_code, resp.text)
        return JsonResponse({'error': 'AI service error'}, status=502)
    
    try:
        data= resp.json()
        ai_reply = data['choices'][0]['message']['content']
    
    except Exception as exc:
        logger.exception("Error processing OpenAI API response: %s", exc)
        return JsonResponse({'error': 'Error processing AI response'}, status=500)

    return JsonResponse({'reply': ai_reply})