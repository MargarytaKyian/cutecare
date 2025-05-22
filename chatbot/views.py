from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import ChatSession, ChatMessage
from decouple import config
import google.generativeai as genai
import json

# --- Конфігурація Gemini API ---
GEMINI_API_KEY = config('GEMINI_API_KEY', default=None)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
SYSTEM_INSTRUCTION = """Ти доброзичливий ветеринарний консультант на ім'я \"PetBot\".
Ти працюєш на сайті \"CuteCare\".
Твоя мета - допомагати власникам домашніх улюбленців.
Ти надаєш первинну консультацію, можеш запитати про породу, вік, симптоми тварини.
Ти можеш рекомендувати загальні поради щодо догляду, харчування.
Якщо ситуація серйозна або потребує огляду, ти завжди наполягаєш на візиті до справжнього ветеринара.
Ти НЕ ставиш точних діагнозів і НЕ призначаєш лікування медикаментами.
Ти можеш рекомендувати зоотовари з сайту \"CuteCare\", якщо це доречно (наприклад, спеціальний корм, вітаміни, засоби для догляду).
Спілкуйся українською мовою. Будь ввічливим, турботливим та професійним.
Уникай фраз на кшталт "Як модель ШІ...". Поводься як справжній консультант.
"""

def get_gemini_model():
    if not GEMINI_API_KEY:
        return None
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction=SYSTEM_INSTRUCTION,
    )
# --- Кінець конфігурації Gemini API ---


@login_required
def chat_home_view(request):
    user_sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
    if user_sessions.exists():
        latest_session = user_sessions.first()
        return redirect('chatbot:chat_session', session_id=latest_session.id)
    context = {
        'user_sessions': user_sessions,
        'active_session': None,
        'chat_messages': [],
        'no_active_chat': True
    }
    return render(request, 'chatbot/chat_page.html', context)


@login_required
def create_new_chat_view(request):
    new_session = ChatSession.objects.create(user=request.user, title="Новий чат")
    return redirect('chatbot:chat_session', session_id=new_session.id)

@login_required
def chat_session_view(request, session_id):
    try:
        active_session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    except Http404:
        return HttpResponseNotFound("Такого чату не знайдено або у вас немає до нього доступу.")

    messages_qs = active_session.messages.all().order_by('timestamp')
    user_sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')

    messages_for_json = []
    for msg in messages_qs:
        messages_for_json.append({
            'sender': msg.sender,
            'text': msg.text,
            'timestamp': msg.timestamp.isoformat() 
        })
    chat_messages_db_json = json.dumps(messages_for_json)

    context = {
        'active_session': active_session,
        'chat_messages_db_json': chat_messages_db_json,
        'user_sessions': user_sessions,
        'no_active_chat': False
    }
    return render(request, 'chatbot/chat_page.html', context)


@login_required
def chat_home_view(request):
    user_sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
    if user_sessions.exists():
        latest_session = user_sessions.first()
        return redirect('chatbot:chat_session', session_id=latest_session.id)
    
    context = {
        'user_sessions': user_sessions,
        'active_session': None,
        'chat_messages_db_json': json.dumps([]),
        'no_active_chat': True
    }
    return render(request, 'chatbot/chat_page.html', context)


@login_required
@require_POST
def send_message_api_view(request, session_id):
    try:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    except Http404:
        return JsonResponse({'error': 'Chat session not found or access denied.'}, status=404)

    try:
        data = json.loads(request.body)
        user_message_text = data.get('message')
        if not user_message_text:
            return JsonResponse({'error': 'Message is required.'}, status=400)

        user_chat_message = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.SENDER_USER,
            text=user_message_text
        )

        history_for_gemini = []
        db_messages = session.messages.all().order_by('timestamp')
        for db_msg in db_messages:
            role = "user" if db_msg.sender == ChatMessage.SENDER_USER else "model"
            history_for_gemini.append({"role": role, "parts": [{"text": db_msg.text}]})
        
        model = get_gemini_model()
        if not model:
            return JsonResponse({'error': 'Gemini API not configured.'}, status=500)

        chat_session_gemini = model.start_chat(history=history_for_gemini[:-1])
        
        try:
            gemini_response = chat_session_gemini.send_message(user_message_text)
            ai_response_text = gemini_response.text
        except Exception as e:
            ai_response_text = f"Вибачте, сталася помилка під час генерації відповіді: {str(e)}"
            print(f"Gemini API error: {e}")

        ai_chat_message = ChatMessage.objects.create(
            session=session,
            sender=ChatMessage.SENDER_AI,
            text=ai_response_text
        )

        session.updated_at = timezone.now()
        if session.title == "Новий чат" or not session.title:
             session.title = user_message_text[:30] + ('...' if len(user_message_text) > 30 else '')
        session.save()

        return JsonResponse({
            'user_message': {
                'text': user_chat_message.text,
                'timestamp': user_chat_message.timestamp.isoformat()
            },
            'ai_message': {
                'text': ai_chat_message.text,
                'timestamp': ai_chat_message.timestamp.isoformat()
            },
            'session_title': session.title
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        print(f"Error in send_message_api_view: {e}")
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    

@login_required
@require_POST
def delete_chat_session_api_view(request, session_id):
    try:
        session_to_delete = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session_to_delete.delete()
        return JsonResponse({'status': 'success', 'message': 'Чат успішно видалено.'})
    except Http404:
        return JsonResponse({'status': 'error', 'message': 'Чат не знайдено або у вас немає доступу.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Помилка видалення чату: {str(e)}'}, status=500)


@login_required
@require_POST
def clear_all_sessions_api_view(request):
    try:
        ChatSession.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success', 'message': 'Вся історія чатів успішно очищена.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Помилка очищення історії: {str(e)}'}, status=500)