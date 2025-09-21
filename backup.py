import os
import shutil
import sqlite3
import json
import zipfile
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, current_app
from flask_login import login_required, current_user
from models import db, BackupLog, SystemSettings, User, Product, Invoice, InvoiceItem, TaxReport
from forms import BackupForm, RestoreForm
from auth import admin_required
import schedule
import time
import threading

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/backup')
@login_required
@admin_required
def backup_dashboard():
    """لوحة تحكم النسخ الاحتياطي"""
    # آخر النسخ الاحتياطية
    recent_backups = BackupLog.query.order_by(BackupLog.created_at.desc()).limit(10).all()
    
    # إحصائيات النسخ الاحتياطي
    total_backups = BackupLog.query.count()
    successful_backups = BackupLog.query.filter_by(status='success').count()
    failed_backups = BackupLog.query.filter_by(status='failed').count()
    
    # حجم قاعدة البيانات
    db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
    db_size = 0
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path)
    
    # إعدادات النسخ الاحتياطي التلقائي
    auto_backup_enabled = SystemSettings.get_setting('auto_backup_enabled', 'false') == 'true'
    backup_frequency = SystemSettings.get_setting('backup_frequency', 'weekly')
    
    return render_template('backup/dashboard.html',
                         recent_backups=recent_backups,
                         total_backups=total_backups,
                         successful_backups=successful_backups,
                         failed_backups=failed_backups,
                         db_size=db_size,
                         auto_backup_enabled=auto_backup_enabled,
                         backup_frequency=backup_frequency)

@backup_bp.route('/backup/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_backup():
    """إنشاء نسخة احتياطية"""
    form = BackupForm()
    
    if form.validate_on_submit():
        try:
            backup_path = perform_backup(
                backup_type=form.backup_type.data,
                include_files=form.include_files.data,
                compress=form.compress.data,
                user_id=current_user.id
            )
            
            if backup_path:
                flash('تم إنشاء النسخة الاحتياطية بنجاح.', 'success')
                return redirect(url_for('backup.backup_dashboard'))
            else:
                flash('فشل في إنشاء النسخة الاحتياطية.', 'error')
        
        except Exception as e:
            flash(f'خطأ في إنشاء النسخة الاحتياطية: {str(e)}', 'error')
    
    return render_template('backup/create.html', form=form)

@backup_bp.route('/backup/restore', methods=['GET', 'POST'])
@login_required
@admin_required
def restore_backup():
    """استعادة نسخة احتياطية"""
    form = RestoreForm()
    
    # قائمة النسخ الاحتياطية المتاحة
    backups_dir = os.path.join('instance', 'backups')
    available_backups = []
    
    if os.path.exists(backups_dir):
        for filename in os.listdir(backups_dir):
            if filename.endswith(('.zip', '.sql', '.json')):
                filepath = os.path.join(backups_dir, filename)
                file_size = os.path.getsize(filepath)
                file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
                available_backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': file_size,
                    'date': file_date
                })
    
    available_backups.sort(key=lambda x: x['date'], reverse=True)
    
    if form.validate_on_submit():
        try:
            backup_file = form.backup_file.data
            restore_type = form.restore_type.data
            
            if not os.path.exists(backup_file):
                flash('ملف النسخة الاحتياطية غير موجود.', 'error')
                return render_template('backup/restore.html', form=form, backups=available_backups)
            
            success = perform_restore(
                backup_file=backup_file,
                restore_type=restore_type,
                user_id=current_user.id
            )
            
            if success:
                flash('تم استعادة النسخة الاحتياطية بنجاح.', 'success')
                return redirect(url_for('backup.backup_dashboard'))
            else:
                flash('فشل في استعادة النسخة الاحتياطية.', 'error')
        
        except Exception as e:
            flash(f'خطأ في استعادة النسخة الاحتياطية: {str(e)}', 'error')
    
    return render_template('backup/restore.html', form=form, backups=available_backups)

@backup_bp.route('/backup/download/<int:backup_id>')
@login_required
@admin_required
def download_backup(backup_id):
    """تحميل نسخة احتياطية"""
    backup_log = BackupLog.query.get_or_404(backup_id)
    
    if not os.path.exists(backup_log.file_path):
        flash('ملف النسخة الاحتياطية غير موجود.', 'error')
        return redirect(url_for('backup.backup_dashboard'))
    
    return send_file(
        backup_log.file_path,
        as_attachment=True,
        download_name=os.path.basename(backup_log.file_path)
    )

@backup_bp.route('/backup/delete/<int:backup_id>', methods=['POST'])
@login_required
@admin_required
def delete_backup(backup_id):
    """حذف نسخة احتياطية"""
    backup_log = BackupLog.query.get_or_404(backup_id)
    
    try:
        # حذف الملف
        if os.path.exists(backup_log.file_path):
            os.remove(backup_log.file_path)
        
        # حذف السجل من قاعدة البيانات
        db.session.delete(backup_log)
        db.session.commit()
        
        flash('تم حذف النسخة الاحتياطية بنجاح.', 'success')
    
    except Exception as e:
        flash(f'خطأ في حذف النسخة الاحتياطية: {str(e)}', 'error')
    
    return redirect(url_for('backup.backup_dashboard'))

@backup_bp.route('/backup/settings', methods=['POST'])
@login_required
@admin_required
def update_backup_settings():
    """تحديث إعدادات النسخ الاحتياطي"""
    auto_backup_enabled = request.form.get('auto_backup_enabled') == 'on'
    backup_frequency = request.form.get('backup_frequency', 'weekly')
    
    SystemSettings.set_setting('auto_backup_enabled', str(auto_backup_enabled).lower(), user_id=current_user.id)
    SystemSettings.set_setting('backup_frequency', backup_frequency, user_id=current_user.id)
    
    # إعادة جدولة النسخ الاحتياطي التلقائي
    schedule_automatic_backups()
    
    flash('تم تحديث إعدادات النسخ الاحتياطي بنجاح.', 'success')
    return redirect(url_for('backup.backup_dashboard'))

def perform_backup(backup_type='full', include_files=True, compress=True, user_id=None):
    """تنفيذ عملية النسخ الاحتياطي"""
    try:
        # إنشاء مجلد النسخ الاحتياطي
        backups_dir = os.path.join('instance', 'backups')
        os.makedirs(backups_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_{backup_type}_{timestamp}'
        
        if backup_type == 'full':
            backup_path = create_full_backup(backups_dir, backup_name, include_files, compress)
        elif backup_type == 'data_only':
            backup_path = create_data_backup(backups_dir, backup_name, compress)
        elif backup_type == 'structure_only':
            backup_path = create_structure_backup(backups_dir, backup_name, compress)
        else:
            raise ValueError(f'نوع النسخ الاحتياطي غير مدعوم: {backup_type}')
        
        # حساب حجم الملف
        file_size = os.path.getsize(backup_path) if os.path.exists(backup_path) else 0
        
        # تسجيل النسخة الاحتياطية
        backup_log = BackupLog(
            backup_type='manual',
            file_path=backup_path,
            file_size=file_size,
            status='success',
            created_by=user_id
        )
        db.session.add(backup_log)
        db.session.commit()
        
        return backup_path
    
    except Exception as e:
        # تسجيل الخطأ
        backup_log = BackupLog(
            backup_type='manual',
            file_path='',
            file_size=0,
            status='failed',
            error_message=str(e),
            created_by=user_id
        )
        db.session.add(backup_log)
        db.session.commit()
        
        raise e

def create_full_backup(backups_dir, backup_name, include_files=True, compress=True):
    """إنشاء نسخة احتياطية كاملة"""
    if compress:
        backup_path = os.path.join(backups_dir, f'{backup_name}.zip')
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # نسخ قاعدة البيانات
            db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            if os.path.exists(db_path):
                zipf.write(db_path, 'database.db')
            
            # نسخ الملفات المرفقة
            if include_files:
                instance_dir = 'instance'
                if os.path.exists(instance_dir):
                    for root, dirs, files in os.walk(instance_dir):
                        for file in files:
                            if not file.endswith('.db'):  # تجنب نسخ قاعدة البيانات مرتين
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, '.')
                                zipf.write(file_path, arcname)
            
            # إضافة معلومات النسخة الاحتياطية
            backup_info = {
                'created_at': datetime.now().isoformat(),
                'backup_type': 'full',
                'include_files': include_files,
                'database_version': get_database_version()
            }
            zipf.writestr('backup_info.json', json.dumps(backup_info, indent=2))
    
    else:
        # نسخ بدون ضغط
        backup_dir = os.path.join(backups_dir, backup_name)
        os.makedirs(backup_dir, exist_ok=True)
        
        # نسخ قاعدة البيانات
        db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        if os.path.exists(db_path):
            shutil.copy2(db_path, os.path.join(backup_dir, 'database.db'))
        
        # نسخ الملفات المرفقة
        if include_files:
            instance_dir = 'instance'
            if os.path.exists(instance_dir):
                shutil.copytree(instance_dir, os.path.join(backup_dir, 'instance'), dirs_exist_ok=True)
        
        backup_path = backup_dir
    
    return backup_path

def create_data_backup(backups_dir, backup_name, compress=True):
    """إنشاء نسخة احتياطية للبيانات فقط"""
    backup_path = os.path.join(backups_dir, f'{backup_name}.json')
    
    # تصدير البيانات إلى JSON
    data = {
        'users': export_table_data(User),
        'products': export_table_data(Product),
        'invoices': export_table_data(Invoice),
        'invoice_items': export_table_data(InvoiceItem),
        'tax_reports': export_table_data(TaxReport),
        'backup_info': {
            'created_at': datetime.now().isoformat(),
            'backup_type': 'data_only',
            'database_version': get_database_version()
        }
    }
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    if compress:
        compressed_path = f'{backup_path}.zip'
        with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, os.path.basename(backup_path))
        os.remove(backup_path)
        backup_path = compressed_path
    
    return backup_path

def create_structure_backup(backups_dir, backup_name, compress=True):
    """إنشاء نسخة احتياطية لهيكل قاعدة البيانات فقط"""
    backup_path = os.path.join(backups_dir, f'{backup_name}.sql')
    
    db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
    
    with sqlite3.connect(db_path) as conn:
        with open(backup_path, 'w', encoding='utf-8') as f:
            # تصدير هيكل قاعدة البيانات
            for line in conn.iterdump():
                if line.startswith('CREATE TABLE') or line.startswith('CREATE INDEX'):
                    f.write(f'{line}\n')
    
    if compress:
        compressed_path = f'{backup_path}.zip'
        with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, os.path.basename(backup_path))
        os.remove(backup_path)
        backup_path = compressed_path
    
    return backup_path

def perform_restore(backup_file, restore_type='full', user_id=None):
    """تنفيذ عملية الاستعادة"""
    try:
        if backup_file.endswith('.zip'):
            return restore_from_zip(backup_file, restore_type)
        elif backup_file.endswith('.json'):
            return restore_from_json(backup_file, restore_type)
        elif backup_file.endswith('.sql'):
            return restore_from_sql(backup_file, restore_type)
        else:
            raise ValueError('تنسيق ملف النسخة الاحتياطية غير مدعوم')
    
    except Exception as e:
        print(f'خطأ في الاستعادة: {str(e)}')
        return False

def restore_from_zip(backup_file, restore_type):
    """استعادة من ملف ZIP"""
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # قراءة معلومات النسخة الاحتياطية
        info_file = os.path.join(temp_dir, 'backup_info.json')
        if os.path.exists(info_file):
            with open(info_file, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)
        
        if restore_type == 'full':
            # استعادة قاعدة البيانات
            db_file = os.path.join(temp_dir, 'database.db')
            if os.path.exists(db_file):
                db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
                shutil.copy2(db_file, db_path)
            
            # استعادة الملفات
            instance_backup = os.path.join(temp_dir, 'instance')
            if os.path.exists(instance_backup):
                if os.path.exists('instance'):
                    shutil.rmtree('instance')
                shutil.copytree(instance_backup, 'instance')
        
        return True

def restore_from_json(backup_file, restore_type):
    """استعادة من ملف JSON"""
    with open(backup_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if restore_type == 'full':
        # حذف البيانات الحالية
        db.drop_all()
        db.create_all()
    
    # استعادة البيانات
    restore_table_data(User, data.get('users', []))
    restore_table_data(Product, data.get('products', []))
    restore_table_data(Invoice, data.get('invoices', []))
    restore_table_data(InvoiceItem, data.get('invoice_items', []))
    restore_table_data(TaxReport, data.get('tax_reports', []))
    
    return True

def restore_from_sql(backup_file, restore_type):
    """استعادة من ملف SQL"""
    db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
    
    with sqlite3.connect(db_path) as conn:
        with open(backup_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        if restore_type == 'full':
            # حذف الجداول الحالية
            conn.executescript('DROP TABLE IF EXISTS users; DROP TABLE IF EXISTS products;')
        
        # تنفيذ سكريبت SQL
        conn.executescript(sql_script)
    
    return True

def export_table_data(model_class):
    """تصدير بيانات جدول إلى قاموس"""
    items = model_class.query.all()
    data = []
    
    for item in items:
        item_dict = {}
        for column in model_class.__table__.columns:
            value = getattr(item, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif hasattr(value, 'value'):  # Enum values
                value = value.value
            item_dict[column.name] = value
        data.append(item_dict)
    
    return data

def restore_table_data(model_class, data):
    """استعادة بيانات جدول من قاموس"""
    for item_data in data:
        # تحويل التواريخ
        for key, value in item_data.items():
            if isinstance(value, str) and 'T' in value:
                try:
                    item_data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
        
        item = model_class(**item_data)
        db.session.add(item)
    
    db.session.commit()

def get_database_version():
    """الحصول على إصدار قاعدة البيانات"""
    try:
        # يمكن إضافة جدول لتتبع إصدار قاعدة البيانات
        return "1.0"
    except:
        return "unknown"

def schedule_automatic_backups():
    """جدولة النسخ الاحتياطي التلقائي"""
    schedule.clear()  # مسح الجدولة السابقة
    
    auto_backup_enabled = SystemSettings.get_setting('auto_backup_enabled', 'false') == 'true'
    if not auto_backup_enabled:
        return
    
    backup_frequency = SystemSettings.get_setting('backup_frequency', 'weekly')
    
    if backup_frequency == 'daily':
        schedule.every().day.at("02:00").do(automatic_backup_job)
    elif backup_frequency == 'weekly':
        schedule.every().sunday.at("02:00").do(automatic_backup_job)
    elif backup_frequency == 'monthly':
        schedule.every().month.do(automatic_backup_job)

def automatic_backup_job():
    """مهمة النسخ الاحتياطي التلقائي"""
    try:
        with current_app.app_context():
            perform_backup(
                backup_type='full',
                include_files=True,
                compress=True,
                user_id=None  # نسخة تلقائية
            )
    except Exception as e:
        print(f'خطأ في النسخ الاحتياطي التلقائي: {str(e)}')

def start_backup_scheduler():
    """بدء مجدول النسخ الاحتياطي"""
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # فحص كل دقيقة
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

# تهيئة الجدولة عند تحميل الوحدة
def init_backup_system(app):
    """تهيئة نظام النسخ الاحتياطي"""
    with app.app_context():
        schedule_automatic_backups()
        start_backup_scheduler()
