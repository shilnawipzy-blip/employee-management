from django.db import models
from designations.models import Designation


class Employee(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    designation = models.ForeignKey(
        Designation,
        on_delete=models.CASCADE
    )

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    photo = models.ImageField(
        upload_to="employees/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name