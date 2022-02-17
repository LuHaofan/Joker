from django.urls import path

from . import views

app_name = "editor"
urlpatterns = [
    path('', views.index, name='index'),
    path('save_note/', views.saveNote, name = 'save_note'),
    path('delete_note/', views.deleteNote, name = 'delete_note'),
    path('bibtex_handler/', views.bibtex_handler, name = 'bibtex_handler'),
    path('save_tag/', views.saveTag, name = 'save_tag')
]