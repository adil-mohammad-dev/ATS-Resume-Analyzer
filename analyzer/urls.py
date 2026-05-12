from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze/', views.analyze_resume, name='analyze_resume'),
    path('result/', views.result_page, name='result_page'),
]