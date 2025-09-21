from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField, IntegerField, DateField, BooleanField, PasswordField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError
from models import User, Product, TaxType, UserRole
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class UserForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6)])
    role = SelectField('الدور', choices=[
        (UserRole.USER.value, 'مستخدم'),
        (UserRole.ACCOUNTANT.value, 'محاسب'),
        (UserRole.ADMIN.value, 'مدير')
    ], validators=[DataRequired()])
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')
    
    def __init__(self, original_user=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_user = original_user
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and (not self.original_user or user.id != self.original_user.id):
            raise ValidationError('اسم المستخدم موجود بالفعل.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and (not self.original_user or user.id != self.original_user.id):
            raise ValidationError('البريد الإلكتروني موجود بالفعل.')

class ProductForm(FlaskForm):
    name = StringField('اسم المنتج', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('الوصف')
    price = DecimalField('السعر', validators=[DataRequired(), NumberRange(min=0)], places=2)
    tax_type = SelectField('نوع الضريبة', choices=[
        (TaxType.VAT.value, 'ضريبة القيمة المضافة (14%)'),
        (TaxType.WITHHOLDING.value, 'ضريبة الخصم والإضافة (5%)')
    ], validators=[DataRequired()])
    tax_rate = DecimalField('معدل الضريبة (%)', validators=[DataRequired(), NumberRange(min=0, max=100)], places=2)
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # تعيين معدلات الضريبة الافتراضية
        if not self.tax_rate.data:
            if self.tax_type.data == TaxType.VAT.value:
                self.tax_rate.data = 14.0
            elif self.tax_type.data == TaxType.WITHHOLDING.value:
                self.tax_rate.data = 5.0

class InvoiceItemForm(FlaskForm):
    product_id = SelectField('المنتج', coerce=int, validators=[DataRequired()])
    quantity = DecimalField('الكمية', validators=[DataRequired(), NumberRange(min=0.001)], places=3)
    unit_price = DecimalField('سعر الوحدة', validators=[DataRequired(), NumberRange(min=0)], places=2)
    discount_percentage = DecimalField('نسبة الخصم (%)', validators=[Optional(), NumberRange(min=0, max=100)], places=2, default=0)
    
    def __init__(self, *args, **kwargs):
        super(InvoiceItemForm, self).__init__(*args, **kwargs)
        self.product_id.choices = [(p.id, f"{p.name} - {p.price} جنيه") 
                                  for p in Product.query.filter_by(is_active=True).all()]

class InvoiceForm(FlaskForm):
    customer_name = StringField('اسم العميل', validators=[DataRequired(), Length(max=200)])
    customer_tax_id = StringField('الرقم الضريبي للعميل', validators=[Optional(), Length(max=50)])
    customer_address = TextAreaField('عنوان العميل')
    invoice_date = DateField('تاريخ الفاتورة', validators=[DataRequired()], default=datetime.today)
    due_date = DateField('تاريخ الاستحقاق', validators=[Optional()])
    notes = TextAreaField('ملاحظات')
    submit = SubmitField('حفظ الفاتورة')

class ReportForm(FlaskForm):
    report_type = SelectField('نوع التقرير', choices=[
        ('monthly', 'شهري'),
        ('quarterly', 'ربع سنوي'),
        ('yearly', 'سنوي'),
        ('custom', 'فترة مخصصة')
    ], validators=[DataRequired()])
    
    period_start = DateField('من تاريخ', validators=[DataRequired()])
    period_end = DateField('إلى تاريخ', validators=[DataRequired()])
    
    include_cancelled = BooleanField('تضمين الفواتير المُلغاة', default=False)
    export_format = SelectField('تنسيق التصدير', choices=[
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('both', 'كلاهما')
    ], default='pdf')
    
    submit = SubmitField('إنشاء التقرير')
    
    def validate_period_end(self, period_end):
        if period_end.data < self.period_start.data:
            raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')

class SearchForm(FlaskForm):
    query = StringField('البحث', validators=[Optional()])
    date_from = DateField('من تاريخ', validators=[Optional()])
    date_to = DateField('إلى تاريخ', validators=[Optional()])
    customer_name = StringField('اسم العميل', validators=[Optional()])
    min_amount = DecimalField('أقل مبلغ', validators=[Optional(), NumberRange(min=0)], places=2)
    max_amount = DecimalField('أكبر مبلغ', validators=[Optional(), NumberRange(min=0)], places=2)
    include_cancelled = BooleanField('تضمين المُلغاة', default=False)
    submit = SubmitField('بحث')

class BackupForm(FlaskForm):
    backup_type = SelectField('نوع النسخة الاحتياطية', choices=[
        ('full', 'نسخة كاملة'),
        ('data_only', 'البيانات فقط'),
        ('structure_only', 'الهيكل فقط')
    ], default='full')
    
    include_files = BooleanField('تضمين الملفات المرفقة', default=True)
    compress = BooleanField('ضغط الملف', default=True)
    submit = SubmitField('إنشاء نسخة احتياطية')

class RestoreForm(FlaskForm):
    backup_file = StringField('ملف النسخة الاحتياطية', validators=[DataRequired()])
    restore_type = SelectField('نوع الاستعادة', choices=[
        ('full', 'استعادة كاملة'),
        ('data_only', 'البيانات فقط'),
        ('merge', 'دمج مع البيانات الحالية')
    ], default='full')
    
    confirm_restore = BooleanField('أؤكد الاستعادة (سيتم حذف البيانات الحالية)', validators=[DataRequired()])
    submit = SubmitField('استعادة')

class SettingsForm(FlaskForm):
    company_name = StringField('اسم الشركة', validators=[DataRequired(), Length(max=200)])
    company_address = TextAreaField('عنوان الشركة')
    company_tax_id = StringField('الرقم الضريبي للشركة', validators=[DataRequired(), Length(max=50)])
    company_phone = StringField('هاتف الشركة', validators=[Optional(), Length(max=20)])
    company_email = StringField('بريد الشركة', validators=[Optional(), Email()])
    
    # إعدادات الضرائب
    default_vat_rate = DecimalField('معدل ضريبة القيمة المضافة الافتراضي (%)', 
                                   validators=[DataRequired(), NumberRange(min=0, max=100)], 
                                   places=2, default=14.0)
    default_withholding_rate = DecimalField('معدل ضريبة الخصم والإضافة الافتراضي (%)', 
                                          validators=[DataRequired(), NumberRange(min=0, max=100)], 
                                          places=2, default=5.0)
    
    # إعدادات النسخ الاحتياطي
    auto_backup_enabled = BooleanField('تفعيل النسخ الاحتياطي التلقائي', default=True)
    backup_frequency = SelectField('تكرار النسخ الاحتياطي', choices=[
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري')
    ], default='weekly')
    
    # إعدادات الفواتير
    invoice_prefix = StringField('بادئة رقم الفاتورة', validators=[Optional(), Length(max=10)], default='INV')
    invoice_start_number = IntegerField('رقم البداية للفواتير', validators=[DataRequired(), NumberRange(min=1)], default=1)
    
    submit = SubmitField('حفظ الإعدادات')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('كلمة المرور الحالية', validators=[DataRequired()])
    new_password = PasswordField('كلمة المرور الجديدة', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('تأكيد كلمة المرور الجديدة', validators=[DataRequired()])
    submit = SubmitField('تغيير كلمة المرور')
    
    def validate_confirm_password(self, confirm_password):
        if confirm_password.data != self.new_password.data:
            raise ValidationError('كلمات المرور غير متطابقة.')

class QuickInvoiceForm(FlaskForm):
    """نموذج مبسط لإنشاء فاتورة سريعة"""
    customer_name = StringField('اسم العميل', validators=[DataRequired()])
    items = FieldList(FormField(InvoiceItemForm), min_entries=1, max_entries=20)
    add_item = SubmitField('إضافة منتج')
    submit = SubmitField('إنشاء الفاتورة')
