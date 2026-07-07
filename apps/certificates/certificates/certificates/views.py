from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from fpdf import FPDF
import os
from .models import Certificate


class CertificatePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'XODIMLAR MALAKASINI OSHIRISH MARKAZI', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Sahifa {self.page_no()}', 0, 0, 'C')


def generate_certificate_pdf(request, certificate_id):
    """Генерация PDF сертификата"""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    pdf = CertificatePDF('L', 'mm', 'A4')  # Landscape
    pdf.add_page()
    
    # Рамка
    pdf.set_draw_color(30, 58, 95)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    
    # Заголовок
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(30, 58, 95)
    pdf.cell(0, 20, 'SERTIFIKAT', 0, 1, 'C')
    pdf.ln(5)
    
    # Подзаголовок
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Malaka oshirishni tasdiqlaydi', 0, 1, 'C')
    pdf.ln(10)
    
    # Текст
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Bu sertifikat berilgan:', 0, 1, 'C')
    pdf.ln(5)
    
    # Имя студента
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(30, 58, 95)
    student_name = certificate.student.full_name or 'Noma\'lum'
    pdf.cell(0, 15, student_name, 0, 1, 'C')
    pdf.ln(5)
    
    # Информация о курсе
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f'{certificate.course.title} kursi bo\'yicha malaka oshirganligini tasdiqlaydi', 0, 1, 'C')
    pdf.cell(0, 10, f'Dars soatlari: {certificate.course.duration_hours} soat', 0, 1, 'C')
    pdf.ln(10)
    
    # Дата и номер
    pdf.set_font('Arial', '', 11)
    issue_date = certificate.issue_date.strftime('%d.%m.%Y')
    expiry_date = certificate.expiry_date.strftime('%d.%m.%Y') if certificate.expiry_date else '5 yil'
    
    pdf.cell(90, 10, f'Berilgan sana: {issue_date}', 0, 0, 'L')
    pdf.cell(90, 10, f'Amal qilish muddati: {expiry_date}', 0, 1, 'R')
    pdf.ln(10)
    
    # Номер сертификата
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, f'Sertifikat raqami: {certificate.certificate_number}', 0, 1, 'R')
    
    # Вывод PDF
    pdf_output = pdf.output()
    
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
