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
    path('proof/<int:note_id>/', views.blockchain_proof, name='blockchain_proof'),
    path('api/blockchain_status/', views.api_blockchain_status, name='api_blockchain_status'),
    
    # Quick Wins Features
    path('pin/<int:note_id>/', views.toggle_pin, name='toggle_pin'),
    path('archive/<int:note_id>/', views.toggle_archive, name='toggle_archive'),
    path('trash/<int:note_id>/', views.trash_note, name='trash_note'),
    path('restore/<int:note_id>/', views.restore_note, name='restore_note'),
    path('color/<int:note_id>/', views.update_color, name='update_color'),
]
