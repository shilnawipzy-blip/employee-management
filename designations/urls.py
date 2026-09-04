from django.urls import path
from . import views

urlpatterns = [
    path('', views.designation_list, name='designation_list'),
    path('add/', views.designation_add, name='designation_add'),
    path('<int:id>/edit/', views.designation_edit, name='designation_edit'),
    path('<int:id>/delete/', views.designation_delete, name='designation_delete'),
]