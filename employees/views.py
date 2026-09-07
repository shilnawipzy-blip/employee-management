from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Employee
from .forms import EmployeeForm
import cv2
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np


def employee_list(request):
    employees = Employee.objects.all()

    return render(
        request,
        'employee_list.html',
        {'employees': employees}
    )


def employee_add(request):

    if request.method == 'POST':

        form = EmployeeForm(
            request.POST,
            request.FILES
        )

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
            request.FILES,
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
    
def employee_checkin(request):

    return render(
        request,
        'employee_checkin.html'
    )
    
@csrf_exempt
def detect_face(request):

    if request.method == 'POST':

        image_data = request.POST.get('image')

        if not image_data:
            return JsonResponse({
                'face_detected': False
            })

        image_data = image_data.split(',')[1]

        image_bytes = base64.b64decode(image_data)

        numpy_array = np.frombuffer(
            image_bytes,
            np.uint8
        )

        image = cv2.imdecode(
            numpy_array,
            cv2.IMREAD_COLOR
        )

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        face_cascade = cv2.CascadeClassifier(
            'employees/cascade/haarcascade_frontalface_default.xml'
        )

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )
        
        print("Faces detected:", len(faces))

        if len(faces) > 1:
            return JsonResponse({
                'face_detected': True,
                'employee_id': None,
                'employee_name': None,
                'error': 'Multiple faces detected. Please ensure only one person is in front of the camera.'
            })

        if len(faces) == 0:
            return JsonResponse({
                'face_detected': False,
                'employee_id': None,
                'employee_name': None
            })

        recognizer = cv2.face.LBPHFaceRecognizer_create()

        training_faces = []
        training_labels = []

        employees = Employee.objects.exclude(
            photo=''
        ).exclude(
            photo__isnull=True
        )

        for employee in employees:

            try:

                stored_image = cv2.imread(
                    employee.photo.path
                )

                if stored_image is None:
                    continue

                stored_gray = cv2.cvtColor(
                    stored_image,
                    cv2.COLOR_BGR2GRAY
                )

                stored_faces = face_cascade.detectMultiScale(
                    stored_gray,
                    scaleFactor=1.1,
                    minNeighbors=5
                )

                for (x, y, w, h) in stored_faces:

                    face = stored_gray[
                        y:y + h,
                        x:x + w
                    ]

                    training_faces.append(face)
                    training_labels.append(employee.id)

            except Exception:
                continue

        if not training_faces:
            return JsonResponse({
                'face_detected': True,
                'employee_id': None,
                'employee_name': None
            })

        recognizer.train(
            training_faces,
            np.array(training_labels)
        )

        x, y, w, h = faces[0]

        detected_face = gray[
            y:y + h,
            x:x + w
        ]

        employee_id, confidence = recognizer.predict(
            detected_face
        )
        
        
        print("Employee ID:", employee_id)
        print("Confidence:", confidence)


        employee = Employee.objects.filter(
            id=employee_id
        ).first()

        if employee and confidence < 80:

            return JsonResponse({
                'face_detected': True,
                'employee_id': employee.id,
                'employee_name': employee.name,
                'email': employee.email,
                'phone': employee.phone,
                'designation': employee.designation.name,
                'photo': employee.photo.url if employee.photo else None,
            })

        return JsonResponse({
            'face_detected': True,
            'employee_id': None,
            'employee_name': None
            
        })

    return JsonResponse({
        'face_detected': False,
        'employee_id': None,
        'employee_name': None
    })
    
