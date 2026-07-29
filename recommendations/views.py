from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .ml_engine import MLEngine
from .models import RecipeFeedback
import json
#smtp
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
engine = MLEngine()

# --- PAGES ---
def home(request): return render(request, 'home.html')

@login_required(login_url='/login/')
def diet_chat(request): return render(request, 'diet_chat.html')

@login_required(login_url='/login/')
def food_chat(request): return render(request, 'food_chat.html')

@login_required(login_url='/login/')
def dashboard_view(request):
    # Fetch liked recipes for the logged-in user
    liked_recipes = RecipeFeedback.objects.filter(user=request.user, action='like').order_by('-timestamp')
    context = {
        'liked_recipes': liked_recipes,
        'like_count': liked_recipes.count()
    }
    return render(request, 'dashboard.html', context)

# --- AUTH (Standard) ---
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard') # Redirect to Dashboard on signup
    else: form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard') # Redirect to Dashboard on login
    else: form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# --- API (Keep existing APIs exactly as they were in V11) ---
@csrf_exempt
def api_diet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            response = engine.recommend_diet(
                data.get('weight'), data.get('target_weight'), data.get('duration'),
                data.get('workout_type'), data.get('age', 25), data.get('sugar', 'no'),
                data.get('diet_style', 'standard'), data.get('food_type', 'All'),
                data.get('lang', 'en')
            )
            return JsonResponse(response)
        except: return JsonResponse({'error': "Server Error"}, status=200)
    return JsonResponse({'error': "Invalid"}, status=400)

@csrf_exempt
def api_food(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_history = []
        if request.user.is_authenticated:
            user_history = list(RecipeFeedback.objects.filter(user=request.user, action='like').values_list('recipe_name', flat=True))
        
        response = engine.recommend_food(
            data.get('query'), data.get('allergies'), data.get('region'),
            data.get('food_type', 'All'), data.get('lang', 'en'), user_history
        )
        return JsonResponse(response)
    return JsonResponse({'error': "Invalid"}, status=400)

@csrf_exempt
def api_feedback(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        # Prevent duplicate likes for the same recipe by the same user
        if not RecipeFeedback.objects.filter(user=request.user, recipe_name=data.get('recipe'), action=data.get('action')).exists():
            RecipeFeedback.objects.create(user=request.user, recipe_name=data.get('recipe'), action=data.get('action'))
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)
def about(request): return render(request, 'about.html')
def services(request): return render(request, 'services.html')



def contact(request):
    if request.method == "POST":
        # 1. Get data matching your HTML input names
        name = request.POST.get("name")
        email = request.POST.get("youremail") # Matches 'youremail' in HTML
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # 2. Validate Email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "❌🫤 Please enter a valid email address.", extra_tags="contact_msg")
            return redirect("contact")

        # 3. Send HTML Confirmation Email to User
        # Make sure you have a 'contacttem.html' file in your templates folder!
        try:
            html_message = render_to_string('contacttem.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'now': timezone.now(),
            })
            
            user_email = EmailMessage(
                subject="🎉👻 Thanks for connecting with us 🫰!",
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            user_email.content_subtype = "html"
            user_email.send(fail_silently=True)

            # 4. Notify Admin (You)
            admin_email = EmailMessage(
                subject="🙋🤝 New Contact Form Submission",
                body=f"New contact received.\n\nName: {name}\nEmail: {email}\nSubject: {subject}\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['yashvardhan282828@gmail.com'], # Your admin email
            )
            admin_email.send(fail_silently=True)

            # 5. Success Message
            messages.success(request, "✨ Thank you for contacting us!", extra_tags="contact_msg")
            
        except Exception as e:
            messages.error(request, "Error sending email. Please try again.", extra_tags="contact_msg")

        return redirect("contact")

    return render(request, "contact.html")