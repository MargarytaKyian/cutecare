from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import ChatSession, ChatMessage
from decouple import config
import google.generativeai as genai
import json


try:
    from main.models import Category, Product
    from django.db.models import Avg, Q, Value, FloatField
    from django.db.models.functions import Coalesce
except ImportError:
    print("ПОПЕРЕДЖЕННЯ: Моделі Category та/або Product з додатка 'main' не знайдено. Рекомендації товарів будуть неможливі.")
    class Category:
        @staticmethod
        def objects_filter(**kwargs): return Category
        def filter(**kwargs): return Category
        def exists(self): return False
    class Product:
        @staticmethod
        def objects_filter(**kwargs): return Product
        def filter(**kwargs): return Product
        def annotate(self, **kwargs): return self
        def order_by(self, *args): return []
        def exists(self): return False
        def get_absolute_url(self): return "#"
        category = type('Category', (), {'name': 'Невідома категорія'})()
        name = "Невідомий товар"
        sell_price = 0.00


try:
    from pets.models import Pet
except ImportError:
    class Pet:
        @staticmethod
        def objects_filter(**kwargs): return Pet
        def filter(**kwargs): return Pet
        def order_by(*args): return []
        def exists(self): return False
        def get_gender_display(self): return "Стать не визначено (помилка моделі)"
        def get_age_display(self): return "Вік не визначено (помилка моделі)"
        def get_weight_display(self): return "Вага не визначено (помилка моделі)"


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


def get_gemini_model(user):
    if not GEMINI_API_KEY:
        return None

    user_name = user.first_name if user.first_name else user.username
    user_context_info = f"Ти спілкуєшся з користувачем на ім'я {user_name}."

    pets_context_info = "Ось інформація про його/її улюбленців, зареєстрованих на сайті:\n"
    
    if hasattr(Pet, 'objects') and callable(getattr(Pet.objects, 'filter', None)):
        user_pets = Pet.objects.filter(owner=user).order_by('name')
        if user_pets.exists():
            for pet_instance in user_pets:
                pets_context_info += f"\n🐾 Кличка: {pet_instance.name}\n"
                pets_context_info += f"   - Вид: {pet_instance.species}\n"
                if pet_instance.breed:
                    pets_context_info += f"   - Порода: {pet_instance.breed}\n"
                else:
                    pets_context_info += f"   - Порода: не вказано\n"
                pets_context_info += f"   - Вік: {pet_instance.get_age_display()}\n"
                pets_context_info += f"   - Вага: {pet_instance.get_weight_display()}\n"
                pets_context_info += f"   - Стать: {pet_instance.get_gender_display()}\n"
                if pet_instance.health_features:
                    pets_context_info += f"   - Особливості здоров'я та характеру: {pet_instance.health_features}\n"
                else:
                    pets_context_info += f"   - Особливості здоров'я та характеру: не вказано\n"
        else:
            pets_context_info += "У користувача наразі не додано інформації про улюбленців на сайті. Якщо це важливо для консультації, ти можеш делікатно запитати про вид, кличку, вік, симптоми тощо.\n"
    else:
         pets_context_info += "Не вдалося завантажити інформацію про улюбленців. Ти можеш делікатно запитати про вид, кличку, вік, симптоми тощо, якщо це потрібно для консультації.\n"

    product_catalog_info = "\n\n🛍️ ІНФОРМАЦІЯ ПРО ЗООТОВАРИ НА САЙТІ 'CuteCare':\n"
    try:
        if not (hasattr(Category, 'objects') and hasattr(Product, 'objects')):
            raise ImportError("Моделі Category або Product не завантажені належним чином (можливо, заглушки).")

        available_categories = Category.objects.filter(available=True)
        if available_categories.exists():
            category_names = ", ".join([cat.name for cat in available_categories])
            product_catalog_info += f"Доступні категорії товарів: {category_names}.\n"
        else:
            product_catalog_info += "Наразі немає доступних категорій товарів на сайті.\n"

        popular_products = Product.objects.filter(available=True) \
            .annotate(avg_rating=Coalesce(Avg('reviewrating__rating', filter=Q(reviewrating__status=True)), Value(0.0), output_field=FloatField())) \
            .order_by('-avg_rating', '-created')[:3]

        if popular_products.exists():
            product_catalog_info += "\nОсь декілька прикладів товарів з нашого асортименту:\n"
            for prod in popular_products:
                relative_url = prod.get_absolute_url() 
                product_catalog_info += (f"- Назва: \"{prod.name}\"\n"
                                         f"  Категорія: {prod.category.name}\n"
                                         f"  Ціна: {prod.sell_price} грн\n"
                                         f"  Опис: {prod.description[:100] + '...' if prod.description and len(prod.description) > 100 else prod.description or 'Опис відсутній.'}\n"
                                         f"  Посилання на сайті CuteCare: {relative_url}\n")
        else:
            product_catalog_info += "Наразі немає вибірки популярних товарів.\n"
        
        product_catalog_info += "\nПам'ятай: ти повинен рекомендувати товари лише тоді, коли це дійсно доречно та відповідає потребам користувача. Завжди надавай посилання на товар на сайті CuteCare."

    except ImportError as e:
        product_catalog_info += f"Не вдалося завантажити інформацію про товари: {e}. Рекомендації товарів недоступні.\n"
        print(f"ПОПЕРЕДЖЕННЯ: {e}")
    except Exception as e:
        product_catalog_info += f"Сталася системна помилка при спробі завантажити інформацію про товари: {e}. Рекомендації товарів тимчасово недоступні.\n"
        print(f"ПОМИЛКА завантаження товарів для Gemini: {e}")

    dynamic_system_instruction = (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"📌 ДОДАТКОВИЙ КОНТЕКСТ ПРО КОРИСТУВАЧА:\n{user_context_info}\n\n"
        f"🐕 ІНФОРМАЦІЯ ПРО УЛЮБЛЕНЦІВ КОРИСТУВАЧА:\n{pets_context_info}\n"
        f"{product_catalog_info}"
    )

    return genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction=dynamic_system_instruction,
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
        'chat_messages_db_json': json.dumps([]), 
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
        
        model = get_gemini_model(request.user) 
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