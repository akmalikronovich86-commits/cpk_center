from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from fpdf import FPDF
import os
from .models import Certificate


class CertificatePDF(FPDF):
    def __init__(self):
        super().__init__('L', 'mm', 'A4')
        # Добавляем шрифт с поддержкой юникода
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/TTF/DejaVuSans.ttf',
        ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break
        
        if font_path:
            self.add_font('DejaVu', '', font_path, uni=True)
            self.add_font('DejaVu', 'B', font_path.replace('.ttf', '-Bold.ttf'), uni=True)
            self.add_font('DejaVu', 'I', font_path.replace('.ttf', '-Oblique.ttf'), uni=True)
            self.font_name = 'DejaVu'
        else:
            self.font_name = 'Helvetica'


def generate_certificate_pdf(request, certificate_id):
    """Генерация PDF сертификата"""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    pdf = CertificatePDF()
    pdf.add_page()
    pdf.set_auto_page_break(False)
    
    fn = pdf.font_name
    
    # Рамка
    pdf.set_draw_color(30, 58, 95)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    
    # Внутренняя рамка
    pdf.set_draw_color(201, 169, 97)
    pdf.set_line_width(0.5)
    pdf.rect(15, 15, 267, 180)
    
    # Заголовок организации
    pdf.set_font(fn, 'B', 14)
    pdf.set_text_color(30, 58, 95)
    pdf.set_y(25)
    pdf.cell(0, 10, 'XODIMLAR MALAKASINI OSHIRISH VA', 0, 1, 'C')
    pdf.cell(0, 10, 'QAYTA TAYYORLASH MARKAZI', 0, 1, 'C')
    pdf.ln(10)
    
    # Заголовок СЕРТИФИКАТ
    pdf.set_font(fn, 'B', 36)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 20, 'SERTIFIKAT', 0, 1, 'C')
    pdf.ln(5)
    
    # Подзаголовок
    pdf.set_font(fn, '', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Malaka oshirishni tasdiqlaydi', 0, 1, 'C')
    pdf.ln(10)
    
    # Текст "Bu sertifikat berilgan"
    pdf.set_font(fn, '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Bu sertifikat berilgan:', 0, 1, 'C')
    pdf.ln(5)
    
    # Имя студента
    pdf.set_font(fn, 'B', 22)
    pdf.set_text_color(30, 58, 95)
    student_name = certificate.student.full_name or "Noma'lum"
    pdf.cell(0, 15, student_name, 0, 1, 'C')
    pdf.ln(5)
    
    # Информация о курсе
    pdf.set_font(fn, '', 12)
    pdf.set_text_color(0, 0, 0)
    course_title = certificate.course.title
    pdf.cell(0, 10, f'"{course_title}" kursi bo\'yicha malaka oshirganligini tasdiqlaydi', 0, 1, 'C')
    pdf.cell(0, 10, f'Dars soatlari: {certificate.course.duration_hours} soat', 0, 1, 'C')
    pdf.ln(15)
    
    # Даты
    pdf.set_font(fn, '', 11)
    issue_date = certificate.issue_date.strftime('%d.%m.%Y')
    expiry_date = certificate.expiry_date.strftime('%d.%m.%Y') if certificate.expiry_date else '5 yil'
    
    y_pos = pdf.get_y()
    pdf.set_xy(20, y_pos)
    pdf.cell(120, 10, f'Berilgan sana: {issue_date}', 0, 0, 'L')
    pdf.cell(120, 10, f'Amal qilish muddati: {expiry_date}', 0, 1, 'R')
    pdf.ln(20)
    
    # Подпись
    pdf.set_font(fn, '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(90, 5, '', 0, 0)
    pdf.cell(90, 5, '_____________________', 0, 1, 'C')
    pdf.cell(90, 5, '', 0, 0)
    pdf.cell(90, 5, 'Markaz direktori', 0, 1, 'C')
    
    # Номер сертификата внизу
    pdf.set_font(fn, 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.set_xy(20, 195)
    pdf.cell(257, 5, f'Sertifikat raqami: {certificate.certificate_number}', 0, 0, 'R')
    
    # QR-код справа внизу (если есть)
    if certificate.qr_image and os.path.exists(certificate.qr_image.path):
        try:
            pdf.image(certificate.qr_image.path, x=240, y=150, w=30)
        except Exception as e:
            pass
    
    # Вывод PDF
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        pdf_output = pdf_output.encode('latin-1')
    
    response = HttpResponse(pdf_output, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.certificate_number}.pdf"'
    
    return response


def verify_certificate(request, qr_code):
    """Страница проверки подлинности сертификата"""
    certificate = get_object_or_404(Certificate, qr_code=qr_code)
    
    context = {
        'certificate': certificate,
        'is_valid': certificate.status == 'issued',
    }
    
    return render(request, 'certificates/verify.html', context)
