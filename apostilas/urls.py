from django.urls import path
from . import views

urlpatterns = [
    path('add_apostila/', views.add_apostila, name='add_apostila'),
    path('apostila/<int:id>/', views.apostila, name='apostila'),
]