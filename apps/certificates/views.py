from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from fpdf import FPDF
import tempfile
import os
import qrcode
import io
from .models import Certificate


class CertificatePDF(FPDF):
    def __init__(self, logo_path=None):
        super().__init__('L', 'mm', 'A4')
        self.font_name = 'Helvetica'
        self.logo_path = logo_path


def generate_certificate_pdf(request, certificate_id):
    """Генерация PDF сертификата"""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    # Генерируем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    
    verify_url = request.build_absolute_uri(f'/certificates/verify/{certificate.qr_code}/')
    qr.add_data(verify_url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as qr_tmp:
        qr_tmp.write(qr_buffer.read())
        qr_path = qr_tmp.name
    
    # Создаем PDF
    pdf = CertificatePDF()
    pdf.add_page()
    pdf.set_auto_page_break(False)
    fn = pdf.font_name
    
    # Рамки
    pdf.set_draw_color(30, 58, 95)
    pdf.set_line_width(3)
    pdf.rect(8, 8, 281, 194)
    
    pdf.set_draw_color(180, 150, 70)
    pdf.set_line_width(0.8)
    pdf.rect(13, 13, 271, 184)
    
    # Логотип (слева вверху)
    if pdf.logo_path and os.path.exists(pdf.logo_path):
        try:
            pdf.image(pdf.logo_path, x=20, y=20, w=30)
        except Exception:
            pass  # Если логотип не загрузился, продолжаем без него
    
    # Декоративная линия
    pdf.set_draw_color(180, 150, 70)
    pdf.set_line_width(0.5)
    pdf.line(80, 42, 217, 42)
    
    # Заголовок организации
    pdf.set_font(fn, 'B', 11)
    pdf.set_text_color(30, 58, 95)
    pdf.set_y(22)
    pdf.cell(0, 7, 'XODIMLAR MALAKASINI OSHIRISH VA', 0, 1, 'C')
    pdf.cell(0, 7, 'QAYTA TAYYORLASH MARKAZI', 0, 1, 'C')
    
    # SERTIFIKAT
    pdf.set_font(fn, 'B', 40)
    pdf.set_text_color(30, 58, 95)
    pdf.set_y(48)
    pdf.cell(0, 22, 'SERTIFIKAT', 0, 1, 'C')
    
    # Линия под SERTIFIKAT
    pdf.set_draw_color(180, 150, 70)
    pdf.set_line_width(0.5)
    pdf.line(100, 72, 197, 72)
    
    # Подзаголовок
    pdf.set_font(fn, '', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.set_y(75)
    pdf.cell(0, 8, 'Malaka oshirishni tasdiqlaydi', 0, 1, 'C')
    
    # "Bu sertifikat berilgan:"
    pdf.set_font(fn, '', 11)
    pdf.set_text_color(80, 80, 80)
    pdf.set_y(90)
    pdf.cell(0, 8, 'Bu sertifikat berilgan:', 0, 1, 'C')
    
    # Имя студента
    pdf.set_font(fn, 'B', 24)
    pdf.set_text_color(30, 58, 95)
    pdf.set_y(100)
    student_name = certificate.student.full_name or "Noma'lum"
    pdf.cell(0, 14, student_name, 0, 1, 'C')
    
    # Линия под именем
    pdf.set_draw_color(180, 150, 70)
    pdf.set_line_width(0.3)
    pdf.line(60, 115, 237, 115)
    
    # Информация о курсе
    pdf.set_font(fn, '', 12)
    pdf.set_text_color(50, 50, 50)
    pdf.set_y(120)
    course_title = certificate.course.title
    pdf.cell(0, 8, '"' + course_title + '"', 0, 1, 'C')
    pdf.cell(0, 8, 'kursi boyicha malaka oshirganligini tasdiqlaydi', 0, 1, 'C')
    pdf.set_font(fn, '', 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, 'Dars soatlari: ' + str(certificate.course.duration_hours) + ' soat', 0, 1, 'C')
    
    # Нижняя часть
    pdf.set_font(fn, '', 10)
    pdf.set_text_color(60, 60, 60)
    issue_date = certificate.issue_date.strftime('%d.%m.%Y')
    if certificate.expiry_date:
        expiry_date = certificate.expiry_date.strftime('%d.%m.%Y')
    else:
        expiry_date = '5 yil'
    
    # Даты слева
    pdf.set_xy(25, 155)
    pdf.cell(80, 7, 'Berilgan sana:', 0, 1, 'L')
    pdf.set_font(fn, 'B', 11)
    pdf.set_text_color(30, 58, 95)
    pdf.set_xy(25, 162)
    pdf.cell(80, 7, issue_date, 0, 1, 'L')
    
    pdf.set_font(fn, '', 10)
    pdf.set_text_color(60, 60, 60)
    pdf.set_xy(25, 172)
    pdf.cell(80, 7, 'Amal qilish muddati:', 0, 1, 'L')
    pdf.set_font(fn, 'B', 11)
    pdf.set_text_color(30, 58, 95)
    pdf.set_xy(25, 179)
    pdf.cell(80, 7, expiry_date, 0, 1, 'L')
    
    # Подпись по центру
    pdf.set_font(fn, '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.set_xy(110, 175)
    pdf.cell(75, 6, '________________________', 0, 1, 'C')
    pdf.set_xy(110, 181)
    pdf.cell(75, 6, 'Markaz direktori', 0, 1, 'C')
    
    # QR-код справа
    pdf.image(qr_path, x=245, y=150, w=28)
    pdf.set_font(fn, '', 7)
    pdf.set_text_color(120, 120, 120)
    pdf.set_xy(240, 180)
    pdf.cell(38, 4, 'Tekshirish uchun', 0, 1, 'C')
    pdf.set_xy(240, 184)
    pdf.cell(38, 4, 'skaner qiling', 0, 1, 'C')
    
    # Номер сертификата
    pdf.set_font(fn, 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.set_xy(20, 193)
    pdf.cell(257, 5, 'Sertifikat raqami: ' + str(certificate.certificate_number), 0, 0, 'C')
    
    # Сохранение PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp_path = tmp.name
        pdf.output(tmp_path)
    
    with open(tmp_path, 'rb') as f:
        pdf_bytes = f.read()
    
    os.unlink(tmp_path)
    os.unlink(qr_path)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = 'certificate_' + str(certificate.certificate_number) + '.pdf'
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    
    return response


def verify_certificate(request, qr_code):
    """Страница проверки подлинности сертификата"""
    certificate = get_object_or_404(Certificate, qr_code=qr_code)
    
    context = {
        'certificate': certificate,
        'is_valid': certificate.status == 'issued',
    }
    
    return render(request, 'certificates/verify.html', context)
