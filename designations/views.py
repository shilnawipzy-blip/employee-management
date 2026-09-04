from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Designation
from .forms import DesignationForm


def designation_list(request):

    designations = Designation.objects.all()

    return render(
        request,
        'designation_list.html',
        {'designations': designations}
    )


def designation_add(request):

    if request.method == 'POST':

        form = DesignationForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Designation created successfully.'
            )

            return redirect('designation_list')

    else:
        form = DesignationForm()

    return render(
        request,
        'designation_add.html',
        {'form': form}
    )


def designation_edit(request, id):

    designation = get_object_or_404(
        Designation,
        id=id
    )

    if request.method == 'POST':

        form = DesignationForm(
            request.POST,
            instance=designation
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Designation updated successfully.'
            )

            return redirect('designation_list')

    else:
        form = DesignationForm(instance=designation)

    return render(
        request,
        'designation_edit.html',
        {'form': form}
    )


def designation_delete(request, id):

    designation = get_object_or_404(
        Designation,
        id=id
    )

    if request.method == 'POST':

        designation.delete()

        messages.success(
            request,
            'Designation deleted successfully.'
        )

        return redirect('designation_list')

    return render(
        request,
        'designation_delete.html',
        {'designation': designation}
    )