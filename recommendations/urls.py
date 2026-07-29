from django.urls import path
from . import views

urlpatterns = [
    # MAIN PAGES
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),       # <--- NEW
    path('services/', views.services, name='services'), # <--- NEW
    path('contact/', views.contact, name='contact'),    # <--- NEW
    
    # APP PAGES
    path('diet/', views.diet_chat, name='diet_chat'),
    path('food/', views.food_chat, name='food_chat'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # AUTH & API (Keep existing lines...)
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('api/diet/', views.api_diet, name='api_diet'),
    path('api/food/', views.api_food, name='api_food'),
    path('api/feedback/', views.api_feedback, name='api_feedback'),
]