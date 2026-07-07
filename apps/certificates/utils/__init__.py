from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_certificate_email(certificate, recipient_email):
    """Отправка email с сертификатом"""
    
    subject = f'Sertifikat: {certificate.certificate_number}'
    
    context = {
        'certificate': certificate,
        'student_name': certificate.student.full_name,
        'course_title': certificate.course.title,
        'issue_date': certificate.issue_date.strftime('%d.%m.%Y'),
        'certificate_number': certificate.certificate_number,
    }
    
    html_message = render_to_string('certificates/email_certificate.html', context)
    plain_message = f"""
    Hurmatli {certificate.student.full_name}!
    
    Sizga {certificate.course.title} kursi bo'yicha sertifikat berildi.
    
    Sertifikat raqami: {certificate.certificate_number}
    Berilgan sana: {certificate.issue_date.strftime('%d.%.%Y')}
    
    Hurmat bilan,
    Xodimlar Malakasini Oshirish Markazi
    """
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )
    
    return True
