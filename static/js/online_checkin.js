const camera = document.getElementById('camera');
const checkInButton = document.getElementById('checkInButton');
const canvas = document.getElementById('canvas');
const message = document.getElementById('cameraMessage');
let stream = null;


checkInButton.addEventListener('click', async function () {

    checkInButton.disabled = true;
    checkInButton.textContent = 'Starting Camera...';
    message.textContent = 'Please wait...';

    try {

        stream = await navigator.mediaDevices.getUserMedia({
            video: true
        });

        camera.srcObject = stream;

        message.textContent =
            'Camera started. Please look at the camera.';

        checkInButton.textContent = 'Checking...';

        setTimeout(checkFace, 1000);

    } catch (error) {

        message.textContent =
            'Camera access denied or unavailable.';

        message.className =
            'mt-3 text-danger';

        checkInButton.disabled = false;
        checkInButton.textContent = 'Check In';

        console.error(error);
    }
});


async function checkFace() {

    if (camera.videoWidth === 0) {
        setTimeout(checkFace, 500);
        return;
    }

    canvas.width = camera.videoWidth;
    canvas.height = camera.videoHeight;

    const context = canvas.getContext('2d');

    context.drawImage(
        camera,
        0,
        0,
        canvas.width,
        canvas.height
    );

    const imageData = canvas.toDataURL('image/jpeg');

    const formData = new FormData();

    formData.append('image', imageData);


    try {

        const response = await fetch(
            detectFaceUrl,
            {
                method: 'POST',

                body: formData,

                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            }
        );


        const data = await response.json();


        if (data.face_detected && data.employee_name) {

            message.textContent =
                '✓ Check In Successful: ' +
                data.employee_name;

            message.className =
                'mt-3 text-success fw-bold';

            checkInButton.textContent =
                'Checked In ✓';


            document.getElementById('employeeInfo').style.display =
                'block';

            document.getElementById('employeeName').textContent =
                data.employee_name;

            document.getElementById('employeeEmail').textContent =
                data.email;

            document.getElementById('employeePhone').textContent =
                data.phone;

            document.getElementById('employeeDesignation').textContent =
                data.designation;


            if (data.photo) {

                document.getElementById('employeePhoto').src =
                    data.photo;

            }


            if (stream) {

                stream.getTracks().forEach(
                    track => track.stop()
                );

            }

            camera.srcObject = null;

        }


        else if (data.face_detected) {

            message.textContent =
                'Face detected, but employee not recognized.';

            message.className =
                'mt-3 text-warning fw-bold';

            checkInButton.disabled = false;

            checkInButton.textContent =
                'Try Again';


            if (stream) {

                stream.getTracks().forEach(
                    track => track.stop()
                );

            }

        }


        else {

            message.textContent =
                'No face detected. Please look at the camera.';

            message.className =
                'mt-3 text-danger';

            checkInButton.disabled = false;

            checkInButton.textContent =
                'Try Again';


            if (stream) {

                stream.getTracks().forEach(
                    track => track.stop()
                );

            }

        }

    } catch (error) {

        console.error(error);

        message.textContent =
            'Something went wrong. Please try again.';

        message.className =
            'mt-3 text-danger';

        checkInButton.disabled = false;

        checkInButton.textContent =
            'Try Again';
    }
}


function getCookie(name) {

    let cookieValue = null;

    if (document.cookie &&
        document.cookie !== '') {

        const cookies =
            document.cookie.split(';');

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + '=')) {

                cookieValue =
                    decodeURIComponent(
                        cookie.substring(
                            name.length + 1
                        )
                    );

                break;
            }
        }
    }

    return cookieValue;
}