"""
مولد PDF احترافي مع دعم العربية الكامل
يدعم جميع التقارير الضريبية بتنسيق مثالي
"""

import os
import io
from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from bidi.algorithm import get_display
import arabic_reshaper

class ArabicPDFGenerator:
    """مولد PDF مع دعم العربية المتقدم"""
    
    def __init__(self):
        self.setup_fonts()
        self.page_width, self.page_height = A4
        self.margin = 2*cm
        
    def setup_fonts(self):
        """إعداد الخطوط العربية"""
        try:
            # محاولة تحميل خط عربي من النظام
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",  # Arial Unicode MS
                "C:/Windows/Fonts/calibri.ttf",  # Calibri
                "C:/Windows/Fonts/tahoma.ttf",   # Tahoma
            ]
            
            font_loaded = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('Arabic', font_path))
                        font_loaded = True
                        break
                    except:
                        continue
            
            if not font_loaded:
                # استخدام خط افتراضي
                self.arabic_font = 'Helvetica'
            else:
                self.arabic_font = 'Arabic'
                
        except Exception as e:
            print(f"خطأ في تحميل الخط: {e}")
            self.arabic_font = 'Helvetica'
    
    def process_arabic_text(self, text):
        """معالجة النص العربي للعرض الصحيح"""
        try:
            if isinstance(text, (int, float, Decimal)):
                return str(text)
            
            if not isinstance(text, str):
                text = str(text)
            
            # إعادة تشكيل النص العربي
            reshaped_text = arabic_reshaper.reshape(text)
            # تطبيق خوارزمية BiDi
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except:
            return str(text)
    
    def safe_float(self, value):
        """تحويل آمن للقيم إلى float"""
        try:
            if isinstance(value, Decimal):
                return float(value)
            elif isinstance(value, (int, float)):
                return float(value)
            else:
                return 0.0
        except:
            return 0.0
    
    def create_header(self, canvas, doc, company_name, tax_number, report_title):
        """إنشاء هيدر احترافي للتقرير"""
        canvas.saveState()
        
        # خلفية الهيدر
        canvas.setFillColor(colors.HexColor('#2c3e50'))
        canvas.rect(0, self.page_height - 3*cm, self.page_width, 3*cm, fill=1)
        
        # عنوان التقرير
        canvas.setFillColor(colors.white)
        canvas.setFont(self.arabic_font, 18)
        title_text = self.process_arabic_text(report_title)
        canvas.drawCentredString(self.page_width/2, self.page_height - 1.5*cm, title_text)
        
        # بيانات الشركة
        canvas.setFont(self.arabic_font, 12)
        company_text = self.process_arabic_text(f"اسم المنشأة: {company_name}")
        tax_text = self.process_arabic_text(f"الرقم الضريبي: {tax_number}")
        
        canvas.drawRightString(self.page_width - self.margin, self.page_height - 2.2*cm, company_text)
        canvas.drawRightString(self.page_width - self.margin, self.page_height - 2.6*cm, tax_text)
        
        # التاريخ
        date_text = self.process_arabic_text(f"تاريخ الإعداد: {datetime.now().strftime('%Y/%m/%d')}")
        canvas.drawString(self.margin, self.page_height - 2.2*cm, date_text)
        
        canvas.restoreState()
    
    def create_footer(self, canvas, doc):
        """إنشاء فوتر احترافي"""
        canvas.saveState()
        
        # خط الفوتر
        canvas.setStrokeColor(colors.HexColor('#2c3e50'))
        canvas.setLineWidth(2)
        canvas.line(self.margin, 2*cm, self.page_width - self.margin, 2*cm)
        
        # نص الفوتر
        canvas.setFillColor(colors.HexColor('#2c3e50'))
        canvas.setFont(self.arabic_font, 10)
        
        footer_text = self.process_arabic_text("نظام إدارة الإقرارات الضريبية - تم الإنشاء تلقائياً")
        canvas.drawCentredString(self.page_width/2, 1.5*cm, footer_text)
        
        # رقم الصفحة
        page_text = self.process_arabic_text(f"صفحة {doc.page}")
        canvas.drawRightString(self.page_width - self.margin, 1.5*cm, page_text)
        
        canvas.restoreState()
    
    def create_summary_table(self, data):
        """إنشاء جدول الملخص"""
        # تحضير البيانات مع التحويل الآمن
        total_sales = self.safe_float(data.get('total_sales', 0))
        vat_sales = self.safe_float(data.get('vat_sales', 0))
        vat_amount = self.safe_float(data.get('vat_amount', 0))
        withholding_sales = self.safe_float(data.get('withholding_sales', 0))
        withholding_amount = self.safe_float(data.get('withholding_amount', 0))
        total_taxes = vat_amount + withholding_amount
        final_total = total_sales + total_taxes
        
        table_data = [
            [self.process_arabic_text("البيان"), self.process_arabic_text("المبلغ (جنيه)")],
            [self.process_arabic_text("إجمالي المبيعات"), f"{total_sales:,.2f}"],
            [self.process_arabic_text("المبيعات الخاضعة لضريبة ق.م.م (14%)"), f"{vat_sales:,.2f}"],
            [self.process_arabic_text("ضريبة القيمة المضافة"), f"{vat_amount:,.2f}"],
            [self.process_arabic_text("المبيعات الخاضعة لضريبة خ.إ (5%)"), f"{withholding_sales:,.2f}"],
            [self.process_arabic_text("ضريبة الخصم والإضافة"), f"{withholding_amount:,.2f}"],
            [self.process_arabic_text("إجمالي الضرائب"), f"{total_taxes:,.2f}"],
            [self.process_arabic_text("الإجمالي النهائي"), f"{final_total:,.2f}"],
        ]
        
        # إنشاء الجدول
        table = Table(table_data, colWidths=[8*cm, 4*cm])
        
        # تنسيق الجدول
        table.setStyle(TableStyle([
            # هيدر الجدول
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # محتوى الجدول
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),  # النص عربي
            ('ALIGN', (1, 1), (1, -1), 'CENTER'), # الأرقام
            
            # الحدود
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c3e50')),
            
            # الصف الأخير (الإجمالي)
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            
            # المسافات
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return table
    
    def create_monthly_table(self, monthly_data):
        """إنشاء جدول البيانات الشهرية"""
        if not monthly_data:
            return None
            
        # تحضير البيانات
        table_data = [
            [
                self.process_arabic_text("الشهر"),
                self.process_arabic_text("المبيعات"),
                self.process_arabic_text("ضريبة ق.م.م"),
                self.process_arabic_text("ضريبة خ.إ"),
                self.process_arabic_text("الإجمالي")
            ]
        ]
        
        for month_data in monthly_data:
            total_sales = self.safe_float(month_data.get('total_sales', 0))
            vat_amount = self.safe_float(month_data.get('vat_amount', 0))
            withholding_amount = self.safe_float(month_data.get('withholding_amount', 0))
            
            if total_sales > 0:  # عرض الشهور التي بها مبيعات فقط
                monthly_total = total_sales + vat_amount + withholding_amount
                table_data.append([
                    self.process_arabic_text(month_data.get('month_name', '')),
                    f"{total_sales:,.0f}",
                    f"{vat_amount:,.0f}",
                    f"{withholding_amount:,.0f}",
                    f"{monthly_total:,.0f}"
                ])
        
        if len(table_data) == 1:  # لا توجد بيانات
            return None
        
        # إنشاء الجدول
        table = Table(table_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm, 3*cm])
        
        # تنسيق الجدول
        table.setStyle(TableStyle([
            # هيدر الجدول
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # محتوى الجدول
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # الشهر
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'), # الأرقام
            
            # الحدود
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c3e50')),
            
            # المسافات
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return table
    
    def generate_tax_declaration_pdf(self, data, filename=None):
        """إنشاء PDF للإقرار الضريبي"""
        if filename is None:
            filename = f"tax_declaration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # إنشاء buffer للـ PDF
        buffer = io.BytesIO()
        
        # إنشاء المستند
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=4*cm,
            bottomMargin=3*cm,
            title=self.process_arabic_text("الإقرار الضريبي")
        )
        
        # قائمة العناصر
        story = []
        
        # إضافة مسافة للهيدر
        story.append(Spacer(1, 1*cm))
        
        # عنوان رئيسي
        title_style = ParagraphStyle(
            'ArabicTitle',
            parent=getSampleStyleSheet()['Title'],
            fontName=self.arabic_font,
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20
        )
        
        title_text = self.process_arabic_text("الإقرار الضريبي السنوي")
        story.append(Paragraph(title_text, title_style))
        
        # جدول الملخص مع التحويل الآمن
        total_sales = self.safe_float(data.get('total_sales', 0))
        vat_sales = self.safe_float(data.get('total_vat_sales', 0))
        vat_amount = self.safe_float(data.get('total_vat_amount', 0))
        withholding_sales = self.safe_float(data.get('total_withholding_sales', 0))
        withholding_amount = self.safe_float(data.get('total_withholding_amount', 0))
        
        summary_data = {
            'total_sales': total_sales,
            'vat_sales': vat_sales,
            'vat_amount': vat_amount,
            'withholding_sales': withholding_sales,
            'withholding_amount': withholding_amount,
            'total_taxes': vat_amount + withholding_amount,
            'final_total': total_sales + vat_amount + withholding_amount
        }
        
        summary_table = self.create_summary_table(summary_data)
        story.append(summary_table)
        story.append(Spacer(1, 1*cm))
        
        # البيانات الشهرية
        if data.get('monthly_data'):
            monthly_title_style = ParagraphStyle(
                'ArabicSubTitle',
                parent=getSampleStyleSheet()['Heading2'],
                fontName=self.arabic_font,
                fontSize=14,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#e74c3c'),
                spaceAfter=15
            )
            
            monthly_title = self.process_arabic_text("التفصيل الشهري")
            story.append(Paragraph(monthly_title, monthly_title_style))
            
            monthly_table = self.create_monthly_table(data['monthly_data'])
            if monthly_table:
                story.append(monthly_table)
        
        # إنشاء الـ PDF مع الهيدر والفوتر
        def add_page_decorations(canvas, doc):
            self.create_header(
                canvas, doc,
                data.get('company_name', 'اسم الشركة'),
                data.get('tax_number', '000000000'),
                "الإقرار الضريبي السنوي"
            )
            self.create_footer(canvas, doc)
        
        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        
        # إرجاع البيانات
        buffer.seek(0)
        return buffer

    def generate_vat_report_pdf(self, data, filename=None):
        """إنشاء PDF لتقرير ضريبة القيمة المضافة"""
        if filename is None:
            filename = f"vat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=self.margin, leftMargin=self.margin,
            topMargin=4*cm, bottomMargin=3*cm,
            title=self.process_arabic_text("تقرير ضريبة القيمة المضافة")
        )
        
        story = []
        story.append(Spacer(1, 1*cm))
        
        # عنوان التقرير
        title_style = ParagraphStyle(
            'ArabicTitle', parent=getSampleStyleSheet()['Title'],
            fontName=self.arabic_font, fontSize=16, alignment=TA_CENTER,
            textColor=colors.HexColor('#3498db'), spaceAfter=20
        )
        title_text = self.process_arabic_text("تقرير ضريبة القيمة المضافة")
        story.append(Paragraph(title_text, title_style))
        
        # جدول الفواتير
        if data.get('invoices'):
            table_data = [
                [self.process_arabic_text("رقم الفاتورة"), self.process_arabic_text("التاريخ"), 
                 self.process_arabic_text("العميل"), self.process_arabic_text("المبلغ الخاضع"), 
                 self.process_arabic_text("الضريبة"), self.process_arabic_text("الإجمالي")]
            ]
            
            for invoice in data['invoices']:
                vat_base = self.safe_float(invoice.vat_amount) / 0.14 if invoice.vat_amount else 0
                table_data.append([
                    invoice.invoice_number,
                    invoice.invoice_date.strftime('%Y/%m/%d'),
                    invoice.customer_name,
                    f"{vat_base:,.2f}",
                    f"{self.safe_float(invoice.vat_amount):,.2f}",
                    f"{self.safe_float(invoice.total_amount):,.2f}"
                ])
            
            table = Table(table_data, colWidths=[3*cm, 2.5*cm, 4*cm, 3*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(table)
        
        def add_page_decorations(canvas, doc):
            self.create_header(canvas, doc, data.get('company_name', 'اسم الشركة'),
                             data.get('tax_number', '000000000'), "تقرير ضريبة القيمة المضافة")
            self.create_footer(canvas, doc)
        
        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer
    
    def generate_withholding_report_pdf(self, data, filename=None):
        """إنشاء PDF لتقرير ضريبة الخصم والإضافة"""
        if filename is None:
            filename = f"withholding_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=self.margin, leftMargin=self.margin,
            topMargin=4*cm, bottomMargin=3*cm,
            title=self.process_arabic_text("تقرير ضريبة الخصم والإضافة")
        )
        
        story = []
        story.append(Spacer(1, 1*cm))
        
        # عنوان التقرير
        title_style = ParagraphStyle(
            'ArabicTitle', parent=getSampleStyleSheet()['Title'],
            fontName=self.arabic_font, fontSize=16, alignment=TA_CENTER,
            textColor=colors.HexColor('#f39c12'), spaceAfter=20
        )
        title_text = self.process_arabic_text("تقرير ضريبة الخصم والإضافة")
        story.append(Paragraph(title_text, title_style))
        
        # جدول الفواتير
        if data.get('invoices'):
            table_data = [
                [self.process_arabic_text("رقم الفاتورة"), self.process_arabic_text("التاريخ"), 
                 self.process_arabic_text("العميل"), self.process_arabic_text("المبلغ الخاضع"), 
                 self.process_arabic_text("الضريبة"), self.process_arabic_text("الإجمالي")]
            ]
            
            for invoice in data['invoices']:
                withholding_base = self.safe_float(invoice.withholding_amount) / 0.05 if invoice.withholding_amount else 0
                table_data.append([
                    invoice.invoice_number,
                    invoice.invoice_date.strftime('%Y/%m/%d'),
                    invoice.customer_name,
                    f"{withholding_base:,.2f}",
                    f"{self.safe_float(invoice.withholding_amount):,.2f}",
                    f"{self.safe_float(invoice.total_amount):,.2f}"
                ])
            
            table = Table(table_data, colWidths=[3*cm, 2.5*cm, 4*cm, 3*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(table)
        
        def add_page_decorations(canvas, doc):
            self.create_header(canvas, doc, data.get('company_name', 'اسم الشركة'),
                             data.get('tax_number', '000000000'), "تقرير ضريبة الخصم والإضافة")
            self.create_footer(canvas, doc)
        
        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer
    
    def generate_comprehensive_report_pdf(self, data, filename=None):
        """إنشاء PDF للتقرير الشامل"""
        if filename is None:
            filename = f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=self.margin, leftMargin=self.margin,
            topMargin=4*cm, bottomMargin=3*cm,
            title=self.process_arabic_text("التقرير الشامل")
        )
        
        story = []
        story.append(Spacer(1, 1*cm))
        
        # عنوان التقرير
        title_style = ParagraphStyle(
            'ArabicTitle', parent=getSampleStyleSheet()['Title'],
            fontName=self.arabic_font, fontSize=16, alignment=TA_CENTER,
            textColor=colors.HexColor('#27ae60'), spaceAfter=20
        )
        title_text = self.process_arabic_text("التقرير الشامل للضرائب والمبيعات")
        story.append(Paragraph(title_text, title_style))
        
        # ملخص الإحصائيات
        summary_data = {
            'total_sales': self.safe_float(data.get('total_sales', 0)),
            'vat_sales': self.safe_float(data.get('vat_taxable_sales', 0)),
            'vat_amount': self.safe_float(data.get('total_vat', 0)),
            'withholding_sales': self.safe_float(data.get('withholding_taxable_sales', 0)),
            'withholding_amount': self.safe_float(data.get('total_withholding', 0)),
        }
        summary_data['total_taxes'] = summary_data['vat_amount'] + summary_data['withholding_amount']
        summary_data['final_total'] = summary_data['total_sales'] + summary_data['total_taxes']
        
        summary_table = self.create_summary_table(summary_data)
        story.append(summary_table)
        
        def add_page_decorations(canvas, doc):
            self.create_header(canvas, doc, data.get('company_name', 'اسم الشركة'),
                             data.get('tax_number', '000000000'), "التقرير الشامل")
            self.create_footer(canvas, doc)
        
        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer
    
    def generate_sales_report_pdf(self, data, filename=None):
        """إنشاء PDF لتقرير المبيعات الصافية"""
        if filename is None:
            filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=self.margin, leftMargin=self.margin,
            topMargin=4*cm, bottomMargin=3*cm,
            title=self.process_arabic_text("تقرير المبيعات الصافية")
        )
        
        story = []
        story.append(Spacer(1, 1*cm))
        
        # عنوان التقرير
        title_style = ParagraphStyle(
            'ArabicTitle', parent=getSampleStyleSheet()['Title'],
            fontName=self.arabic_font, fontSize=16, alignment=TA_CENTER,
            textColor=colors.HexColor('#e74c3c'), spaceAfter=20
        )
        title_text = self.process_arabic_text("تقرير المبيعات الصافية")
        story.append(Paragraph(title_text, title_style))
        
        # ملخص المبيعات
        total_sales = self.safe_float(data.get('total_sales', 0))
        total_vat = self.safe_float(data.get('total_vat', 0))
        total_withholding = self.safe_float(data.get('total_withholding', 0))
        total_taxes = self.safe_float(data.get('total_taxes', 0))
        final_total = total_sales + total_taxes  # المبيعات + الضرائب
        
        summary_data = [
            [self.process_arabic_text("البيان"), self.process_arabic_text("المبلغ (جنيه)")],
            [self.process_arabic_text("المبيعات الأساسية (بدون ضرائب)"), f"{total_sales:,.2f}"],
            [self.process_arabic_text("ضريبة القيمة المضافة"), f"{total_vat:,.2f}"],
            [self.process_arabic_text("ضريبة الخصم والإضافة"), f"{total_withholding:,.2f}"],
            [self.process_arabic_text("إجمالي الضرائب"), f"{total_taxes:,.2f}"],
            [self.process_arabic_text("الإجمالي النهائي (مبيعات + ضرائب)"), f"{final_total:,.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[8*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c3e50')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 1*cm))
        
        # جدول الفواتير التفصيلي
        if data.get('invoices'):
            # عنوان فرعي
            subtitle_style = ParagraphStyle(
                'ArabicSubTitle', parent=getSampleStyleSheet()['Heading2'],
                fontName=self.arabic_font, fontSize=14, alignment=TA_CENTER,
                textColor=colors.HexColor('#e74c3c'), spaceAfter=15
            )
            subtitle_text = self.process_arabic_text("تفاصيل الفواتير")
            story.append(Paragraph(subtitle_text, subtitle_style))
            
            table_data = [
                [self.process_arabic_text("رقم الفاتورة"), self.process_arabic_text("التاريخ"), 
                 self.process_arabic_text("العميل"), self.process_arabic_text("المبيعات"), 
                 self.process_arabic_text("الضرائب"), self.process_arabic_text("الإجمالي")]
            ]
            
            for invoice in data['invoices']:
                taxes = self.safe_float(invoice.vat_amount) + self.safe_float(invoice.withholding_amount)
                table_data.append([
                    invoice.invoice_number,
                    invoice.invoice_date.strftime('%Y/%m/%d'),
                    invoice.customer_name,
                    f"{self.safe_float(invoice.subtotal):,.2f}",
                    f"{taxes:,.2f}",
                    f"{self.safe_float(invoice.total_amount):,.2f}"
                ])
            
            # إضافة صف الإجماليات
            total_sales = sum(self.safe_float(inv.subtotal) for inv in data['invoices'])
            total_taxes = sum(self.safe_float(inv.vat_amount) + self.safe_float(inv.withholding_amount) for inv in data['invoices'])
            total_amount = sum(self.safe_float(inv.total_amount) for inv in data['invoices'])
            
            table_data.append([
                self.process_arabic_text("الإجماليات"), "", "",
                f"{total_sales:,.2f}",
                f"{total_taxes:,.2f}",
                f"{total_amount:,.2f}"
            ])
            
            table = Table(table_data, colWidths=[3*cm, 2.5*cm, 4*cm, 3*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                # تنسيق صف الإجماليات
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTSIZE', (0, -1), (-1, -1), 10),
            ]))
            story.append(table)
        
        def add_page_decorations(canvas, doc):
            self.create_header(canvas, doc, data.get('company_name', 'اسم الشركة'),
                             data.get('tax_number', '000000000'), "تقرير المبيعات الصافية")
            self.create_footer(canvas, doc)
        
        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer
    
    def generate_yearly_summary_pdf(self, data, filename=None):
        """إنشاء PDF للملخص السنوي"""
        if filename is None:
            filename = f"yearly_summary_{data.get('year', 2025)}.pdf"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=self.margin, leftMargin=self.margin,
            topMargin=4*cm, bottomMargin=3*cm,
            title=self.process_arabic_text(f"الملخص السنوي {data.get('year', 2025)}")
        )
        
        story = []
        story.append(Spacer(1, 1*cm))
        
        # عنوان التقرير
        title_style = ParagraphStyle(
            'ArabicTitle', parent=getSampleStyleSheet()['Title'],
            fontName=self.arabic_font, fontSize=18, alignment=TA_CENTER,
            textColor=colors.HexColor('#8e44ad'), spaceAfter=20
        )
        title_text = self.process_arabic_text(f"الملخص السنوي {data.get('year', 2025)}")
        story.append(Paragraph(title_text, title_style))
        
        # الملخص العام
        year_stats = data.get('year_stats', {})
        summary_data = [
            [self.process_arabic_text("البيان"), self.process_arabic_text("القيمة")],
            [self.process_arabic_text("إجمالي الفواتير"), str(year_stats.get('total_invoices', 0))],
            [self.process_arabic_text("إجمالي المبيعات"), f"{self.safe_float(year_stats.get('total_sales', 0)):,.2f} جنيه"],
            [self.process_arabic_text("إجمالي ضريبة ق.م.م"), f"{self.safe_float(year_stats.get('total_vat', 0)):,.2f} جنيه"],
            [self.process_arabic_text("إجمالي ضريبة خ.إ"), f"{self.safe_float(year_stats.get('total_withholding', 0)):,.2f} جنيه"],
            [self.process_arabic_text("إجمالي الضرائب"), f"{self.safe_float(year_stats.get('total_taxes', 0)):,.2f} جنيه"],
            [self.process_arabic_text("الإجمالي النهائي"), f"{self.safe_float(year_stats.get('total_revenue', 0)):,.2f} جنيه"],
        ]
        
        summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c3e50')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 1*cm))
        
        # التفصيل الشهري
        if data.get('monthly_stats'):
            monthly_title_style = ParagraphStyle(
                'ArabicSubTitle', parent=getSampleStyleSheet()['Heading2'],
                fontName=self.arabic_font, fontSize=14, alignment=TA_CENTER,
                textColor=colors.HexColor('#8e44ad'), spaceAfter=15
            )
            monthly_title = self.process_arabic_text("التفصيل الشهري")
            story.append(Paragraph(monthly_title, monthly_title_style))
            
            monthly_data = [
                [self.process_arabic_text("الشهر"), self.process_arabic_text("الفواتير"), 
                 self.process_arabic_text("المبيعات"), self.process_arabic_text("ض.ق.م.م"), 
                 self.process_arabic_text("ض.خ.إ"), self.process_arabic_text("الإجمالي")]
            ]
            
            for month_stat in data['monthly_stats']:
                if month_stat.get('invoices_count', 0) > 0:  # عرض الشهور التي بها بيانات فقط
                    monthly_data.append([
                        self.process_arabic_text(month_stat.get('month_name', '')),
                        str(month_stat.get('invoices_count', 0)),
                        f"{self.safe_float(month_stat.get('sales', 0)):,.0f}",
                        f"{self.safe_float(month_stat.get('vat', 0)):,.0f}",
                        f"{self.safe_float(month_stat.get('withholding', 0)):,.0f}",
                        f"{self.safe_float(month_stat.get('revenue', 0)):,.0f}"
                    ])
            
            if len(monthly_data) > 1:  # إذا كان هناك بيانات شهرية
                monthly_table = Table(monthly_data, colWidths=[3*cm, 2*cm, 3*cm, 2.5*cm, 2.5*cm, 3*cm])
                monthly_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c3e50')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(monthly_table)
                story.append(Spacer(1, 1*cm))
        
        # إحصائيات إضافية
        if data.get('top_months'):
            stats_title_style = ParagraphStyle(
                'ArabicSubTitle', parent=getSampleStyleSheet()['Heading2'],
                fontName=self.arabic_font, fontSize=14, alignment=TA_CENTER,
                textColor=colors.HexColor('#e67e22'), spaceAfter=15
            )
            stats_title = self.process_arabic_text("أفضل الشهور في المبيعات")
            story.append(Paragraph(stats_title, stats_title_style))
            
            top_months_data = [
                [self.process_arabic_text("الترتيب"), self.process_arabic_text("الشهر"), 
                 self.process_arabic_text("المبيعات (جنيه)")]
            ]
            
            for i, month in enumerate(data['top_months'][:5], 1):  # أفضل 5 شهور
                top_months_data.append([
                    str(i),
                    self.process_arabic_text(month.get('month_name', '')),
                    f"{self.safe_float(month.get('sales', 0)):,.0f}"
                ])
            
            top_months_table = Table(top_months_data, colWidths=[2*cm, 6*cm, 6*cm])
            top_months_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e67e22')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c3e50')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(top_months_table)
        
        def add_page_decorations(canvas, doc):
            self.create_header(canvas, doc, data.get('company_name', 'اسم الشركة'),
                             data.get('tax_number', '000000000'), f"الملخص السنوي {data.get('year', 2025)}")
            self.create_footer(canvas, doc)
        
        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer

# إنشاء مثيل عام للاستخدام
pdf_generator = ArabicPDFGenerator()
