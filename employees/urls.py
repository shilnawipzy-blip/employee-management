from django.urls import path
from .views import (employee_list,
                    employee_add,
                    employee_edit,
                    employee_detail,
                    employee_delete,
                    employee_checkin,
                    detect_face
                    )

urlpatterns = [
    path('employees/', employee_list, name='employee_list'),
    path('employees/add/', employee_add, name='employee_add'),
    path('employees/<int:id>/edit/', employee_edit, name='employee_edit'),
    path('employees/<int:id>/', employee_detail, name='employee_detail'),
    path('employees/<int:id>/delete/', employee_delete, name='employee_delete'),
    path('checkin/', employee_checkin, name='employee_checkin'),
    path('checkin/detect-face/', detect_face, name='detect_face'),
]