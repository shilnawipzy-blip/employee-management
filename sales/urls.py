from django.urls import path
from . import views


urlpatterns = [
    path('', views.sales_list, name='sales_list'),
    path('upload/', views.sales_upload, name='sales_upload'),
]