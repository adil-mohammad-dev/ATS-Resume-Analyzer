from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze/', views.analyze_resume, name='analyze_resume'),
    path('result/', views.result_page, name='result_page'),

    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('build-resume/', views.build_resume, name='build_resume'),
    path('builder-result/', views.builder_result, name='builder_result'),
]