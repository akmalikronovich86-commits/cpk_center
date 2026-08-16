from django.conf import settings
from django.db import models


class ZoomAccount(models.Model):
    name = models.CharField("Nomi", max_length=100)
    account_id = models.CharField("Account ID", max_length=100, unique=True)
    client_id = models.CharField("Client ID", max_length=100)
    client_secret = models.CharField("Client Secret", max_length=200)
    is_active = models.BooleanField("Faol", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Zoom Hisob "
        verbose_name_plural = "Onlayn uchrashuv tashkil etish va Akkaunt sozlamalari"

    def __str__(self):
        return self.name


class ZoomMeeting(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Rejalashtirilgan'),
        ('live', 'Jonli efirda'),
        ('completed', 'Tugallangan'),
        ('cancelled', 'Bekor qilingan'),
    ]

    RECURRENCE_CHOICES = [
        ('none', 'Yoq'),
        ('daily', 'Kunlik'),
        ('weekly', 'Haftalik'),
        ('monthly', 'Oylik'),
    ]

    schedule = models.ForeignKey(
        'schedules.Schedule',
        on_delete=models.CASCADE,
        related_name='zoom_meetings',
        verbose_name="Dars jadvali",
        null=True, blank=True
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='zoom_meetings',
        verbose_name="Kurs",
        null=True, blank=True
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='zoom_meetings',
        verbose_name="Oqituvchi "
    )

    zoom_account = models.ForeignKey(
        ZoomAccount,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Zoom hisob"
    )
    zoom_meeting_id = models.CharField("Zoom Meeting ID", max_length=100, blank=True)
    zoom_join_url = models.URLField("Qoshilish URL", blank=True)
    zoom_start_url = models.URLField("Boshlash URL", blank=True)
    zoom_password = models.CharField("Parol", max_length=50, blank=True)

    topic = models.CharField("Mavzu", max_length=300)
    start_time = models.DateTimeField("Boshlanish vaqti")
    duration = models.PositiveIntegerField("Davomiyligi (daqiqa)", default=60)
    recurrence = models.CharField("Takrorlanish", max_length=20, choices=RECURRENCE_CHOICES, default='none')

    waiting_room = models.BooleanField("Kutish xonasi", default=True)
    join_before_host = models.BooleanField("Hostdan oldin qoshilish", default=False)
    mute_upon_entry = models.BooleanField("Kirganda ovozni ochirish", default=True)
    auto_recording = models.CharField(
        "Avtomatik yozish",
        max_length=20,
        choices=[('cloud', 'Bulutda'), ('local', 'Lokal'), ('none', 'Yoq')],
        default='cloud'
    )

    status = models.CharField("Holat", max_length=20, choices=STATUS_CHOICES, default='scheduled')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Zoom Uchrashuv "
        verbose_name_plural = "Zoom orqali onlayn uchrashuv"
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.topic} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"

    @property
    def is_live(self):
        return self.status == 'live'


class ZoomMeetingParticipant(models.Model):
    meeting = models.ForeignKey(ZoomMeeting, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField("Email")
    full_name = models.CharField("Toliq ism", max_length=200)
    join_time = models.DateTimeField(null=True, blank=True)
    leave_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Ishtirokchi "
        verbose_name_plural = "Ishtirokchilar"

    def __str__(self):
        return f"{self.full_name} - {self.meeting.topic}"


class ZoomRecording(models.Model):
    meeting = models.ForeignKey(ZoomMeeting, on_delete=models.CASCADE, related_name='recordings')
    recording_url = models.URLField("Yozish URL")
    download_url = models.URLField("Yuklab olish URL", blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    file_size_mb = models.FloatField(default=0)
    recording_type = models.CharField(
        max_length=20,
        choices=[('shared_screen', 'Ekran'), ('speaker_view', 'Spiker'), ('gallery_view', 'Galereya'), ('audio_only', 'Faqat audio')]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Zoom Yozuv "
        verbose_name_plural = "Onlayn uchrashuvlar yozuvlari"

    def __str__(self):
        return f"{self.meeting.topic} - {self.recording_type}"
