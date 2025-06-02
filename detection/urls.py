from django.urls import path
from .views import check_model_status

urlpatterns = [
    path('check-model/', check_model_status, name='check_model_status'),
]