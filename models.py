from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    USER = "user"

class TaxType(Enum):
    VAT = "vat"  # ضريبة القيمة المضافة 14%
    WITHHOLDING = "withholding"  # ضريبة الخصم والإضافة 5%

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # العلاقات
    invoices = db.relationship('Invoice', foreign_keys='Invoice.created_by', backref='created_by_user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, action):
        """فحص الصلاحيات"""
        permissions = {
            UserRole.ADMIN: [
                'create_invoice', 'edit_invoice', 'delete_invoice', 'view_invoice',
                'create_product', 'edit_product', 'delete_product', 'view_product',
                'create_user', 'edit_user', 'delete_user', 'view_user',
                'view_reports', 'export_reports', 'backup_system', 'restore_system',
                'manage_settings'
            ],
            UserRole.ACCOUNTANT: [
                'create_invoice', 'edit_invoice', 'view_invoice',
                'create_product', 'edit_product', 'view_product',
                'view_reports', 'export_reports'
            ],
            UserRole.USER: [
                'create_invoice', 'view_invoice',
                'view_product'
            ]
        }
        return action in permissions.get(self.role, [])
    
    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    tax_type = db.Column(db.Enum(TaxType), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), nullable=False)  # معدل الضريبة
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    invoice_items = db.relationship('InvoiceItem', backref='product', lazy=True)
    
    def get_tax_amount(self, base_amount):
        """حساب مبلغ الضريبة"""
        return base_amount * (self.tax_rate / 100)
    
    def get_total_with_tax(self, base_amount):
        """حساب المبلغ الإجمالي مع الضريبة"""
        return base_amount + self.get_tax_amount(base_amount)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_tax_id = db.Column(db.String(50))
    customer_address = db.Column(db.Text)
    invoice_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    due_date = db.Column(db.Date)
    
    # المبالغ
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)  # المبلغ قبل الضريبة
    vat_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)  # ضريبة القيمة المضافة
    withholding_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)  # ضريبة الخصم والإضافة
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)  # المبلغ الإجمالي
    
    # معلومات إضافية
    notes = db.Column(db.Text)
    is_cancelled = db.Column(db.Boolean, default=False)
    cancelled_at = db.Column(db.DateTime)
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def calculate_totals(self):
        """حساب إجماليات الفاتورة"""
        self.subtotal = 0
        self.vat_amount = 0
        self.withholding_amount = 0
        
        for item in self.items:
            item_total = item.quantity * item.unit_price
            self.subtotal += item_total
            
            if item.product.tax_type == TaxType.VAT:
                self.vat_amount += item.product.get_tax_amount(item_total)
            elif item.product.tax_type == TaxType.WITHHOLDING:
                self.withholding_amount += item.product.get_tax_amount(item_total)
        
        self.total_amount = self.subtotal + self.vat_amount + self.withholding_amount
    
    def cancel_invoice(self, user_id):
        """إلغاء الفاتورة"""
        self.is_cancelled = True
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by = user_id
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Numeric(10, 3), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    
    def get_line_total(self):
        """حساب إجمالي السطر"""
        base_amount = self.quantity * self.unit_price
        discount_amount = base_amount * (self.discount_percentage / 100)
        return base_amount - discount_amount
    
    def get_tax_amount(self):
        """حساب ضريبة السطر"""
        line_total = self.get_line_total()
        return self.product.get_tax_amount(line_total)
    
    def __repr__(self):
        return f'<InvoiceItem {self.product.name} x {self.quantity}>'

class TaxReport(db.Model):
    __tablename__ = 'tax_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # monthly, quarterly, yearly
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # إجماليات الضرائب
    total_sales = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    total_vat = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    total_withholding = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    
    # معلومات التقرير
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(500))  # مسار ملف التقرير المُصدَّر
    
    def __repr__(self):
        return f'<TaxReport {self.report_type} {self.period_start} - {self.period_end}>'

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(500))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default_value=None):
        setting = SystemSettings.query.filter_by(key=key).first()
        return setting.value if setting else default_value
    
    @staticmethod
    def set_setting(key, value, description=None, user_id=None):
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_by = user_id
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(
                key=key,
                value=value,
                description=description,
                updated_by=user_id
            )
            db.session.add(setting)
        db.session.commit()
        return setting

class BackupLog(db.Model):
    __tablename__ = 'backup_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    backup_type = db.Column(db.String(50), nullable=False)  # manual, automatic
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger)
    status = db.Column(db.String(20), nullable=False)  # success, failed
    error_message = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BackupLog {self.backup_type} {self.status}>'
