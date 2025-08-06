from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from . import camera
import cv2
import time
from app.suggest import autocorrect  # Import the autocorrect function

def home(request):
    return render(request, 'predict.html')

def start_camera(request):
    camera.start_prediction()
    return JsonResponse({'status': 'started'})

def stop_camera(request):
    camera.stop_prediction()
    return JsonResponse({'status': 'stopped'})

def get_word(request):
    word = camera.get_current_word()
    return JsonResponse({'word': word})

def reset_word(request):
    camera.reset_word()
    return JsonResponse({'status': 'reset'})

def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type="multipart/x-mixed-replace; boundary=frame")

def gen_frames():
    while True:
        frame = camera.get_frame()
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)  # Avoid busy-waiting

def get_suggestions(request):
    query_word = request.GET.get('word', '')  # Get the word from the request
    if query_word:
        suggestions = autocorrect(query_word)  # Get suggestions
        suggestions_list = suggestions['word'].tolist()  # Convert to a list
        return JsonResponse({'suggestions': suggestions_list})
    return JsonResponse({'suggestions': []})

