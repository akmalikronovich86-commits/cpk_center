from django.conf import settings
from django.core.mail import send_mail


def send_certificate_email(certificate, recipient_email):
    """Отправка email с уведомлением о сертификате"""

    subject = f'Sertifikat berildi: {certificate.certificate_number}'

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
            <h2 style="color: #1e3a5f; text-align: center;">XODIMLAR MALAKASINI OSHIRISH MARKAZI</h2>
            <hr style="border: 1px solid #1e3a5f; margin: 20px 0;">
            <p style="font-size: 16px;">Hurmatli {certificate.student.full_name}!</p>
            <p>Sizga quyidagi ma'lumotlar bo'yicha sertifikat berildi:</p>
            <div style="background: #f7fafc; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Sertifikat raqami:</strong> {certificate.certificate_number}</p>
                <p><strong>Kurs:</strong> {certificate.course.title}</p>
                <p><strong>Berilgan sana:</strong> {certificate.issue_date.strftime('%d.%m.%Y')}</p>
            </div>
            <p>Sertifikatni tekshirish uchun QR-kodni skaner qiling.</p>
            <hr style="border: 1px solid #e2e8f0; margin: 30px 0;">
            <p style="color: #718096; font-size: 12px; text-align: center;">
                © 2026 Xodimlar Malakasini Oshirish va Qayta Tayyorlash Markazi
            </p>
        </div>
    </body>
    </html>
    """

    plain_message = f"""
    Hurmatli {certificate.student.full_name}!
    Sizga {certificate.course.title} kursi bo'yicha sertifikat berildi.
    Sertifikat raqami: {certificate.certificate_number}
    Berilgan sana: {certificate.issue_date.strftime('%d.%m.%Y')}
    Hurmat bilan, Xodimlar Malakasini Oshirish Markazi
    """

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@cpk.uz'),
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email yuborishda xatolik: {e}")
        return False


def send_credentials_email(user, password):
    """Отправка email с логином и паролем для входа в личный кабинет"""
    from django.conf import settings
    from django.core.mail import send_mail

    if not user.email:
        print(f"⚠️ Email не указан для {user.username}")
        return False

    subject = "CPK Center - Shaxsiy kabinetga kirish ma'lumotlari"

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
            <h2 style="color: #1e3a5f; text-align: center;">XODIMLAR MALAKASINI OSHIRISH MARKAZI</h2>
            <hr style="border: 1px solid #1e3a5f; margin: 20px 0;">
            
            <p style="font-size: 16px;">Hurmatli {user.full_name or user.username}!</p>
            
            <p>Sizning shaxsiy kabinetingiz yaratildi. Quyidagi ma'lumotlar orqali tizimga kiring:</p>
            
            <div style="background: #f7fafc; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Login:</strong> <code style="background: #e2e8f0; padding: 5px 10px; border-radius: 3px;">{user.username}</code></p>
                <p><strong>Parol:</strong> <code style="background: #e2e8f0; padding: 5px 10px; border-radius: 3px;">{password}</code></p>
            </div>
            
            <p style="margin: 20px 0;">
                <a href="http://localhost:8000/login/" style="display: inline-block; padding: 12px 25px; background: #1e3a5f; color: white; text-decoration: none; border-radius: 5px;">
                    Shaxsiy kabinetga kirish
                </a>
            </p>
            
            <p style="color: #e53e3e; font-size: 14px;">
                <strong>Muhim:</strong> Birinchi kirishdan so'ng parolni o'zgartirishni unutmang!
            </p>
            
            <hr style="border: 1px solid #e2e8f0; margin: 30px 0;">
            <p style="color: #718096; font-size: 12px; text-align: center;">
                © 2026 Xodimlar Malakasini Oshirish va Qayta Tayyorlash Markazi
            </p>
        </div>
    </body>
    </html>
    """

    plain_message = f"""
    Hurmatli {user.full_name or user.username}!
    
    Sizning shaxsiy kabinetingiz yaratildi.
    
    Login: {user.username}
    Parol: {password}
    
    Kirish uchun: http://localhost:8000/login/
    
    Muhim: Birinchi kirishdan so'ng parolni o'zgartirishni unutmang!
    
    Hurmat bilan,
    Xodimlar Malakasini Oshirish Markazi
    """

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@cpk.uz'),
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(f"✅ Email yuborildi: {user.email}")
        return True
    except Exception as e:
        print(f"❌ Email yuborishda xatolik: {e}")
        return False
