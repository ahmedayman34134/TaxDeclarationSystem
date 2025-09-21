from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, timedelta
from decimal import Decimal
import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# استيراد النماذج والوحدات
from models import db, User, Product, Invoice, InvoiceItem, TaxType, UserRole, SystemSettings
from forms import ProductForm, InvoiceForm, InvoiceItemForm, SearchForm, SettingsForm
from auth import auth_bp, init_default_users, permission_required
from reports import reports_bp
from backup import backup_bp, init_backup_system

def create_app():
    app = Flask(__name__)
    
    # إعدادات التطبيق
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # تكوين قاعدة البيانات
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # تحويل postgres:// إلى postgresql:// للتوافق مع SQLAlchemy الحديث
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///tax_system.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)  # انتهاء الجلسة بعد 8 ساعات
    
    # إنشاء مجلد instance إذا لم يكن موجوداً
    os.makedirs('instance', exist_ok=True)
    
    # تهيئة قاعدة البيانات
    db.init_app(app)
    
    # تهيئة نظام تسجيل الدخول
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = "strong"  # حماية قوية للجلسة
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # تسجيل البلوبرينتس
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(backup_bp, url_prefix='/backup')

    # إضافة فلاتر مخصصة للقوالب
    @app.template_filter('vat_base')
    def vat_base_filter(amount):
        """حساب المبلغ قبل ضريبة القيمة المضافة"""
        if amount and amount > 0:
            return float(Decimal(str(amount)) / Decimal('0.14'))
        return 0

    @app.template_filter('withholding_base')
    def withholding_base_filter(amount):
        """حساب المبلغ قبل ضريبة الخصم والإضافة"""
        if amount and amount > 0:
            return float(Decimal(str(amount)) / Decimal('0.05'))
        return 0
    
    # إنشاء الجداول وتهيئة البيانات الأساسية
    # معالج الأخطاء
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    # الصفحة الرئيسية
    @app.route('/')
    def index():
        """الصفحة الرئيسية"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    with app.app_context():
        db.create_all()
        init_default_users()
        init_default_settings()
        init_backup_system(app)
    
    return app

def init_default_settings():
    """تهيئة الإعدادات الافتراضية"""
    default_settings = [
        ('company_name', 'شركة الإقرارات الضريبية', 'اسم الشركة'),
        ('company_address', 'القاهرة، مصر', 'عنوان الشركة'),
        ('company_tax_id', '123456789', 'الرقم الضريبي للشركة'),
        ('default_vat_rate', '14.0', 'معدل ضريبة القيمة المضافة الافتراضي'),
        ('default_withholding_rate', '5.0', 'معدل ضريبة الخصم والإضافة الافتراضي'),
        ('invoice_prefix', 'INV', 'بادئة رقم الفاتورة'),
        ('invoice_start_number', '1', 'رقم البداية للفواتير'),
        ('auto_backup_enabled', 'true', 'تفعيل النسخ الاحتياطي التلقائي'),
        ('backup_frequency', 'weekly', 'تكرار النسخ الاحتياطي')
    ]
    
    for key, value, description in default_settings:
        if not SystemSettings.query.filter_by(key=key).first():
            SystemSettings.set_setting(key, value, description)

# إنشاء التطبيق
app = create_app()

@app.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم الرئيسية"""
    # إحصائيات سريعة
    today = datetime.now().date()
    current_month_start = today.replace(day=1)
    
    # إحصائيات اليوم
    today_invoices = Invoice.query.filter(
        Invoice.invoice_date == today,
        Invoice.is_cancelled == False
    ).count()
    
    today_sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
        Invoice.invoice_date == today,
        Invoice.is_cancelled == False
    ).scalar() or 0
    
    # إحصائيات الشهر
    month_invoices = Invoice.query.filter(
        Invoice.invoice_date >= current_month_start,
        Invoice.is_cancelled == False
    ).count()
    
    month_sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
        Invoice.invoice_date >= current_month_start,
        Invoice.is_cancelled == False
    ).scalar() or 0
    
    # إجمالي المنتجات النشطة
    active_products = Product.query.filter_by(is_active=True).count()
    
    # آخر الفواتير
    recent_invoices = Invoice.query.filter_by(is_cancelled=False).order_by(
        Invoice.created_at.desc()
    ).limit(5).all()
    
    # المنتجات الأكثر مبيعاً هذا الشهر
    top_products = db.session.query(
        Product.name,
        db.func.sum(InvoiceItem.quantity).label('total_quantity'),
        db.func.sum(InvoiceItem.quantity * InvoiceItem.unit_price).label('total_amount')
    ).join(InvoiceItem).join(Invoice).filter(
        Invoice.invoice_date >= current_month_start,
        Invoice.is_cancelled == False
    ).group_by(Product.id, Product.name).order_by(
        db.func.sum(InvoiceItem.quantity * InvoiceItem.unit_price).desc()
    ).limit(5).all()
    
    # بيانات المبيعات اليومية (آخر 7 أيام)
    daily_sales_data = []
    daily_sales_labels = []
    
    for i in range(6, -1, -1):  # آخر 7 أيام
        day = today - timedelta(days=i)
        daily_sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
            Invoice.invoice_date == day,
            Invoice.is_cancelled == False
        ).scalar() or 0
        
        daily_sales_data.append(float(daily_sales))
        daily_sales_labels.append(day.strftime('%Y/%m/%d'))
    
    # بيانات الضرائب الشهرية
    month_vat = db.session.query(db.func.sum(Invoice.vat_amount)).filter(
        Invoice.invoice_date >= current_month_start,
        Invoice.is_cancelled == False
    ).scalar() or 0
    
    month_withholding = db.session.query(db.func.sum(Invoice.withholding_amount)).filter(
        Invoice.invoice_date >= current_month_start,
        Invoice.is_cancelled == False
    ).scalar() or 0
    
    tax_data = [float(month_vat), float(month_withholding)]
    tax_labels = ['ضريبة القيمة المضافة', 'ضريبة الخصم والإضافة']
    
    return render_template('dashboard.html',
                         today_invoices=today_invoices,
                         today_sales=today_sales,
                         month_invoices=month_invoices,
                         month_sales=month_sales,
                         active_products=active_products,
                         recent_invoices=recent_invoices,
                         top_products=top_products,
                         daily_sales_data=daily_sales_data,
                         daily_sales_labels=daily_sales_labels,
                         tax_data=tax_data,
                         tax_labels=tax_labels)

# إدارة المنتجات
@app.route('/products')
@login_required
@permission_required('view_product')
def products_list():
    """قائمة المنتجات"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    tax_type = request.args.get('tax_type', '')
    
    query = Product.query
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    if tax_type:
        query = query.filter(Product.tax_type == TaxType(tax_type))
    
    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('products/list.html', products=products, search=search, tax_type=tax_type)

@app.route('/products/new', methods=['GET', 'POST'])
@login_required
@permission_required('create_product')
def create_product():
    """إنشاء منتج جديد"""
    form = ProductForm()
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            tax_type=TaxType(form.tax_type.data),
            tax_rate=form.tax_rate.data,
            is_active=form.is_active.data
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash(f'تم إنشاء المنتج "{product.name}" بنجاح.', 'success')
        return redirect(url_for('products_list'))
    
    return render_template('products/form.html', form=form, title='إضافة منتج جديد')

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('edit_product')
def edit_product(product_id):
    """تعديل منتج"""
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.tax_type = TaxType(form.tax_type.data)
        product.tax_rate = form.tax_rate.data
        product.is_active = form.is_active.data
        
        db.session.commit()
        flash(f'تم تحديث المنتج "{product.name}" بنجاح.', 'success')
        return redirect(url_for('products_list'))
    
    return render_template('products/form.html', form=form, product=product, title='تعديل المنتج')

@app.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
@permission_required('delete_product')
def delete_product(product_id):
    """حذف منتج"""
    product = Product.query.get_or_404(product_id)
    
    # التحقق من وجود فواتير مرتبطة بالمنتج
    if product.invoice_items:
        flash('لا يمكن حذف المنتج لوجود فواتير مرتبطة به.', 'error')
        return redirect(url_for('products_list'))
    
    product_name = product.name
    db.session.delete(product)
    db.session.commit()
    
    flash(f'تم حذف المنتج "{product_name}" بنجاح.', 'success')
    return redirect(url_for('products_list'))

# إدارة الفواتير
@app.route('/invoices')
@login_required
@permission_required('view_invoice')
def invoices_list():
    """قائمة الفواتير"""
    page = request.args.get('page', 1, type=int)
    search_form = SearchForm()
    
    query = Invoice.query
    
    # تطبيق فلاتر البحث
    if request.args.get('query'):
        search_term = request.args.get('query')
        query = query.filter(
            db.or_(
                Invoice.invoice_number.contains(search_term),
                Invoice.customer_name.contains(search_term)
            )
        )
    
    if request.args.get('date_from'):
        date_from = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d').date()
        query = query.filter(Invoice.invoice_date >= date_from)
    
    if request.args.get('date_to'):
        date_to = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d').date()
        query = query.filter(Invoice.invoice_date <= date_to)
    
    if not request.args.get('include_cancelled'):
        query = query.filter(Invoice.is_cancelled == False)
    
    invoices = query.order_by(Invoice.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('invoices/list.html', invoices=invoices, search_form=search_form)

@app.route('/invoices/new', methods=['GET', 'POST'])
@login_required
@permission_required('create_invoice')
def create_invoice():
    """إنشاء فاتورة جديدة"""
    form = InvoiceForm()
    
    if form.validate_on_submit():
        # إنشاء رقم فاتورة تلقائي
        invoice_prefix = SystemSettings.get_setting('invoice_prefix', 'INV')
        last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
        next_number = (last_invoice.id + 1) if last_invoice else int(SystemSettings.get_setting('invoice_start_number', '1'))
        invoice_number = f"{invoice_prefix}-{next_number:06d}"
        
        invoice = Invoice(
            invoice_number=invoice_number,
            customer_name=form.customer_name.data,
            customer_tax_id=form.customer_tax_id.data,
            customer_address=form.customer_address.data,
            invoice_date=form.invoice_date.data,
            due_date=form.due_date.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        flash(f'تم إنشاء الفاتورة "{invoice.invoice_number}" بنجاح.', 'success')
        return redirect(url_for('edit_invoice', invoice_id=invoice.id))
    
    return render_template('invoices/form.html', form=form, title='إنشاء فاتورة جديدة')

@app.route('/invoices/<int:invoice_id>')
@login_required
@permission_required('view_invoice')
def view_invoice(invoice_id):
    """عرض فاتورة"""
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('invoices/view.html', invoice=invoice)

@app.route('/invoices/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('edit_invoice')
def edit_invoice(invoice_id):
    """تعديل فاتورة"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    if invoice.is_cancelled:
        flash('لا يمكن تعديل فاتورة ملغاة.', 'error')
        return redirect(url_for('view_invoice', invoice_id=invoice_id))
    
    form = InvoiceForm(obj=invoice)
    
    if form.validate_on_submit():
        invoice.customer_name = form.customer_name.data
        invoice.customer_tax_id = form.customer_tax_id.data
        invoice.customer_address = form.customer_address.data
        invoice.invoice_date = form.invoice_date.data
        invoice.due_date = form.due_date.data
        invoice.notes = form.notes.data
        
        db.session.commit()
        flash(f'تم تحديث الفاتورة "{invoice.invoice_number}" بنجاح.', 'success')
        return redirect(url_for('view_invoice', invoice_id=invoice_id))
    
    return render_template('invoices/edit.html', form=form, invoice=invoice)

@app.route('/invoices/<int:invoice_id>/items/add', methods=['GET', 'POST'])
@login_required
@permission_required('edit_invoice')
def add_invoice_item(invoice_id):
    """إضافة منتج للفاتورة"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    if invoice.is_cancelled:
        flash('لا يمكن تعديل فاتورة ملغاة.', 'error')
        return redirect(url_for('view_invoice', invoice_id=invoice_id))
    
    form = InvoiceItemForm()
    
    if form.validate_on_submit():
        item = InvoiceItem(
            invoice_id=invoice_id,
            product_id=form.product_id.data,
            quantity=form.quantity.data,
            unit_price=form.unit_price.data,
            discount_percentage=form.discount_percentage.data or 0
        )
        
        db.session.add(item)
        
        # إعادة حساب إجماليات الفاتورة
        invoice.calculate_totals()
        db.session.commit()
        
        flash('تم إضافة المنتج للفاتورة بنجاح.', 'success')
        return redirect(url_for('view_invoice', invoice_id=invoice_id))
    
    return render_template('invoices/add_item.html', form=form, invoice=invoice)

@app.route('/invoices/<int:invoice_id>/items/<int:item_id>/delete', methods=['POST'])
@login_required
@permission_required('edit_invoice')
def delete_invoice_item(invoice_id, item_id):
    """حذف منتج من الفاتورة"""
    invoice = Invoice.query.get_or_404(invoice_id)
    item = InvoiceItem.query.get_or_404(item_id)
    
    if invoice.is_cancelled:
        flash('لا يمكن تعديل فاتورة ملغاة.', 'error')
        return redirect(url_for('view_invoice', invoice_id=invoice_id))
    
    if item.invoice_id != invoice_id:
        flash('المنتج غير موجود في هذه الفاتورة.', 'error')
        return redirect(url_for('view_invoice', invoice_id=invoice_id))
    
    db.session.delete(item)
    
    # إعادة حساب إجماليات الفاتورة
    invoice.calculate_totals()
    db.session.commit()
    
    flash('تم حذف المنتج من الفاتورة بنجاح.', 'success')
    return redirect(url_for('view_invoice', invoice_id=invoice_id))

@app.route('/invoices/<int:invoice_id>/cancel', methods=['POST'])
@login_required
@permission_required('delete_invoice')
def cancel_invoice(invoice_id):
    """إلغاء فاتورة"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    if invoice.is_cancelled:
        flash('الفاتورة ملغاة بالفعل.', 'warning')
        return redirect(url_for('view_invoice', invoice_id=invoice_id))
    
    invoice.cancel_invoice(current_user.id)
    db.session.commit()
    
    flash(f'تم إلغاء الفاتورة "{invoice.invoice_number}" بنجاح.', 'success')
    return redirect(url_for('invoices_list'))

# API endpoints
@app.route('/api/products/<int:product_id>')
@login_required
def api_get_product(product_id):
    """الحصول على بيانات منتج"""
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'tax_type': product.tax_type.value,
        'tax_rate': float(product.tax_rate)
    })

@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    """إحصائيات لوحة التحكم"""
    today = datetime.now().date()
    current_month_start = today.replace(day=1)
    
    # بيانات آخر 7 أيام
    daily_stats = []
    for i in range(7):
        date = today - timedelta(days=i)
        day_invoices = Invoice.query.filter(
            Invoice.invoice_date == date,
            Invoice.is_cancelled == False
        ).all()
        
        daily_stats.append({
            'date': date.isoformat(),
            'invoices_count': len(day_invoices),
            'total_sales': float(sum(inv.total_amount for inv in day_invoices)),
            'vat_amount': float(sum(inv.vat_amount for inv in day_invoices)),
            'withholding_amount': float(sum(inv.withholding_amount for inv in day_invoices))
        })
    
    return jsonify(list(reversed(daily_stats)))

# إعدادات النظام
@app.route('/settings', methods=['GET', 'POST'])
@login_required
@permission_required('manage_settings')
def system_settings():
    """إعدادات النظام"""
    form = SettingsForm()
    
    # تحميل القيم الحالية
    if request.method == 'GET':
        form.company_name.data = SystemSettings.get_setting('company_name', '')
        form.company_address.data = SystemSettings.get_setting('company_address', '')
        form.company_tax_id.data = SystemSettings.get_setting('company_tax_id', '')
        form.company_phone.data = SystemSettings.get_setting('company_phone', '')
        form.company_email.data = SystemSettings.get_setting('company_email', '')
        form.default_vat_rate.data = float(SystemSettings.get_setting('default_vat_rate', '14.0'))
        form.default_withholding_rate.data = float(SystemSettings.get_setting('default_withholding_rate', '5.0'))
        form.auto_backup_enabled.data = SystemSettings.get_setting('auto_backup_enabled', 'false') == 'true'
        form.backup_frequency.data = SystemSettings.get_setting('backup_frequency', 'weekly')
        form.invoice_prefix.data = SystemSettings.get_setting('invoice_prefix', 'INV')
        form.invoice_start_number.data = int(SystemSettings.get_setting('invoice_start_number', '1'))
    
    if form.validate_on_submit():
        # حفظ الإعدادات
        settings_to_save = [
            ('company_name', form.company_name.data),
            ('company_address', form.company_address.data),
            ('company_tax_id', form.company_tax_id.data),
            ('company_phone', form.company_phone.data),
            ('company_email', form.company_email.data),
            ('default_vat_rate', str(form.default_vat_rate.data)),
            ('default_withholding_rate', str(form.default_withholding_rate.data)),
            ('auto_backup_enabled', str(form.auto_backup_enabled.data).lower()),
            ('backup_frequency', form.backup_frequency.data),
            ('invoice_prefix', form.invoice_prefix.data),
            ('invoice_start_number', str(form.invoice_start_number.data))
        ]
        
        for key, value in settings_to_save:
            SystemSettings.set_setting(key, value, user_id=current_user.id)
        
        flash('تم حفظ الإعدادات بنجاح.', 'success')
        return redirect(url_for('system_settings'))
    
    return render_template('settings.html', form=form)

# إنشاء التطبيق
app = create_app()

if __name__ == '__main__':
    # تكوين البورت للإنتاج (Railway) أو التطوير
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
