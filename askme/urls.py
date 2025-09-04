from django.urls import path
from . import views

app_name = 'askme'

urlpatterns = [
    path('', views.home, name='home'),
    path('conversations/', views.conversation_list, name='conversation_list'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation'),
    path('questions/<int:question_id>/', views.question_detail, name='detail'),
    path('questions/<int:question_id>/status/', views.check_status, name='check_status'),
    path('debug-api-keys/', views.debug_api_keys, name='debug-api-keys'),
]