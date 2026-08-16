from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@shared_task
def send_certificate_email(certificate_id, email):
    """Отправка PDF-сертификата на email (вызывать после выпуска)."""
    from .models import Certificate
    cert = Certificate.objects.get(id=certificate_id)
    html = render_to_string('certificates/email_certificate.html', {'certificate': cert})
    msg = EmailMultiAlternatives(
        subject=f"Sertifikat {cert.certificate_number}",
        body=f"Sertifikat {cert.certificate_number} tayyor.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    msg.attach_alternative(html, 'text/html')
    if cert.pdf_file:
        msg.attach(cert.pdf_file.name, cert.pdf_file.read(), 'application/pdf')
    msg.send()
    return certificate_id
