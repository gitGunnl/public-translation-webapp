from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('download_docx/', views.download_docx, name='download_docx'),
]