from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ZoomMeeting
from .services import ZoomAPIClient
import hmac
import hashlib
import base64
import time
import json


@login_required
def meeting_room(request, meeting_id):
    meeting = get_object_or_404(ZoomMeeting, id=meeting_id)
    zoom_config = getattr(settings, "ZOOM_CONFIG", {"CLIENT_ID": "", "CLIENT_SECRET": ""})
    signature = generate_signature(
        meeting.zoom_meeting_id,
        zoom_config.get("CLIENT_ID", ""),
        zoom_config.get("CLIENT_SECRET", "")
    )
    context = {
        "meeting": meeting,
        "signature": signature,
        "user_name": request.user.full_name if hasattr(request.user, "full_name") else request.user.username,
        "user_email": request.user.email,
        "api_key": zoom_config.get("CLIENT_ID", ""),
    }
    return render(request, "zoom_integration/meeting_room.html", context)


@login_required
def meeting_list(request):
    user = request.user
    is_teacher = getattr(user, "role", None) == "teacher" or user.is_staff
    if is_teacher:
        meetings = ZoomMeeting.objects.filter(teacher=user)
    else:
        meetings = ZoomMeeting.objects.filter(
            schedule__group__students=user
        ).distinct()
    context = {"meetings": meetings.order_by("-start_time")}
    return render(request, "zoom_integration/meeting_list.html", context)


@login_required
def create_meeting_from_schedule(request, schedule_id):
    from schedules.models import Schedule
    from .services import MeetingService
    schedule = get_object_or_404(Schedule, id=schedule_id)
    zoom_account = ZoomMeeting.objects.first()
    if not zoom_account:
        return JsonResponse({"error": "Zoom hisob topilmadi"}, status=400)
    service = MeetingService(zoom_account)
    meeting = service.create_meeting_for_schedule(schedule, request.user)
    return JsonResponse({
        "success": True,
        "meeting_id": meeting.id,
        "join_url": meeting.zoom_join_url,
        "meeting_room_url": f"/zoom/meeting/{meeting.id}/"
    })


def generate_signature(meeting_number, api_key, api_secret):
    key = api_secret.encode()
    message = {
        "appKey": api_key,
        "meetingNumber": meeting_number,
        "role": 0,
        "userId": 0,
        "iat": int(time.time()) * 1000,
        "exp": int(time.time()) * 1000 + 60 * 60 * 1000
    }
    message_str = json.dumps(message, separators=(",", ":"))
    signature = base64.b64encode(
        hmac.new(key, message_str.encode(), hashlib.sha256).digest()
    ).decode()
    return signature


@csrf_exempt
@login_required
def webhook(request):
    if request.method == "POST":
        payload = request.body.decode()
        signature = request.headers.get("X-Zoom-Signature")
        client = ZoomAPIClient()
        zoom_config = getattr(settings, "ZOOM_CONFIG", {"CLIENT_SECRET": ""})
        if client.verify_webhook(payload, request.headers.get("X-Zoom-Request-Timestamp"), 
                                 zoom_config.get("CLIENT_SECRET", ""), signature):
            data = json.loads(payload)
            event = data.get("event")
            if event == "meeting.ended":
                meeting_id = data.get("payload", {}).get("object", {}).get("id")
                try:
                    meeting = ZoomMeeting.objects.get(zoom_meeting_id=str(meeting_id))
                    meeting.status = "completed"
                    meeting.save()
                except ZoomMeeting.DoesNotExist:
                    pass
            elif event == "recording.completed":
                meeting_id = data.get("payload", {}).get("object", {}).get("id")
                try:
                    meeting = ZoomMeeting.objects.get(zoom_meeting_id=str(meeting_id))
                    service = MeetingService(meeting.zoom_account)
                    service.get_meeting_recordings(meeting)
                except ZoomMeeting.DoesNotExist:
                    pass
            return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)
