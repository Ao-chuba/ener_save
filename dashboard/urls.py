from django.urls import path
from . import views

urlpatterns = [
    # Authentication routes
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Data entry routes
    path('household/', views.data_entry_household, name='household'),
    path('appliances/', views.data_entry_appliances, name='appliances'),
    path('bill/', views.data_entry_bill, name='bill'),
    
    # Results and tips
    path('results/', views.results, name='results'),
    path('tips/', views.tips, name='tips'),
    
    # AJAX endpoints
    path('delete-appliance/<int:pk>/', views.delete_appliance, name='delete_appliance'),
    
    # Redirect root to login
    path('', views.login_view, name='login'),
    path('gemini_chat/', views.gemini_chat, name='gemini_chat'),
]