from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Employee
from .forms import EmployeeForm


def employee_list(request):
    employees = Employee.objects.all()

    return render(
        request,
        'employee_list.html',
        {'employees': employees}
    )


def employee_add(request):

    if request.method == 'POST':

        form = EmployeeForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Employee created successfully.'
            )

            return redirect('/employees/')

    else:
        form = EmployeeForm()

    return render(
        request,
        'employee_add.html',
        {'form': form}
    )


def employee_edit(request, id):

    employee = Employee.objects.get(id=id)

    if request.method == 'POST':

        form = EmployeeForm(
            request.POST,
            instance=employee
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Employee updated successfully.'
            )

            return redirect('employee_detail', id=employee.id)

    else:
        form = EmployeeForm(instance=employee)

    return render(
        request,
        'employee_edit.html',
        {'form': form}
    )
        
def employee_detail(request, id):

    employee = Employee.objects.get(id=id)

    return render(
        request,
        'employee_detail.html',
        {'employee': employee}
    )
    
def employee_delete(request, id):

    employee = Employee.objects.get(id=id)

    if request.method == 'POST':

        employee.delete()

        messages.success(
            request,
            'Employee deleted successfully.'
        )

        return redirect('/employees/')

    return render(
        request,
        'employee_delete.html',
        {'employee': employee}
    )