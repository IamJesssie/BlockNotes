from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('landing/', views.landing_page, name='landing_page'),
    path('create/', views.create_note_view, name='create_note'),
    path('', views.list_notes, name='list_notes'),
    path('edit/<int:note_id>/', views.edit_note, name='edit_note'),
    path('delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('verify/<int:note_id>/', views.verify_receipt, name='verify_receipt'),
    path('api/blockchain_status/', views.api_blockchain_status, name='api_blockchain_status'),
]