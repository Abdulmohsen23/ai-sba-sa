from django.urls import path
from . import views

app_name = 'program_ideation'

urlpatterns = [
    path('', views.home, name='home'),
    path('language/', views.select_language, name='select_language'),
    path('<int:idea_id>/start/', views.start_ideation, name='start'),
    path('<int:idea_id>/specific/', views.specific_idea, name='specific_idea'),
    path('<int:idea_id>/missing/', views.missing_data, name='missing_data'),
    path('<int:idea_id>/no-specific/', views.no_specific_idea, name='no_specific_idea'),
    path('<int:idea_id>/suggestions/', views.suggestions, name='suggestions'),
    path('<int:idea_id>/complete/', views.complete, name='complete'),
    path('list/', views.idea_list, name='idea_list'),
    path('<int:idea_id>/notes/', views.note_list, name='note_list'),
    path('<int:idea_id>/notes/add/', views.add_note, name='add_note'),
    path('notes/<int:note_id>/', views.note_detail, name='note_detail'),
    path('notes/<int:note_id>/apply/', views.apply_note_suggestion, name='apply_note_suggestion'),
    path('<int:idea_id>/export/pdf/', views.export_idea_pdf, name='export_pdf'),
    path('<int:idea_id>/export/word/', views.export_idea_word, name='export_word'),
]