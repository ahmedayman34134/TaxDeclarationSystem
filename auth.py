from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import User, UserRole, db
from forms import LoginForm, UserForm, ChangePasswordForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

def permission_required(permission):
    """ديكوريتر للتحقق من الصلاحيات"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('يجب تسجيل الدخول أولاً.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not current_user.has_permission(permission):
                flash('ليس لديك صلاحية للوصول إلى هذه الصفحة.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """ديكوريتر للتحقق من صلاحيات المدير"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('هذه الصفحة مخصصة للمديرين فقط.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data) and user.is_active:
            # تحديث آخر تسجيل دخول
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=form.remember_me.data)
            
            # إعادة التوجيه إلى الصفحة المطلوبة أو لوحة التحكم
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard')
            
            flash(f'مرحباً {user.username}!', 'success')
            return redirect(next_page)
        else:
            flash('بيانات الدخول غير صحيحة أو الحساب غير مفعل.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/users')
@login_required
@admin_required
def users_list():
    """قائمة المستخدمين"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('auth/users_list.html', users=users)

@auth_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """إنشاء مستخدم جديد"""
    form = UserForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=UserRole(form.role.data),
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'تم إنشاء المستخدم {user.username} بنجاح.', 'success')
        return redirect(url_for('auth.users_list'))
    
    return render_template('auth/user_form.html', form=form, title='إنشاء مستخدم جديد')

@auth_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """تعديل مستخدم"""
    user = User.query.get_or_404(user_id)
    form = UserForm(original_user=user, obj=user)
    
    # إزالة حقل كلمة المرور من التعديل
    del form.password
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = UserRole(form.role.data)
        user.is_active = form.is_active.data
        
        db.session.commit()
        flash(f'تم تحديث بيانات المستخدم {user.username} بنجاح.', 'success')
        return redirect(url_for('auth.users_list'))
    
    return render_template('auth/user_form.html', form=form, user=user, title='تعديل المستخدم')

@auth_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """حذف مستخدم"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص.', 'error')
        return redirect(url_for('auth.users_list'))
    
    # التحقق من وجود فواتير مرتبطة بالمستخدم
    if user.invoices:
        flash('لا يمكن حذف المستخدم لوجود فواتير مرتبطة به.', 'error')
        return redirect(url_for('auth.users_list'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'تم حذف المستخدم {username} بنجاح.', 'success')
    return redirect(url_for('auth.users_list'))

@auth_bp.route('/profile')
@login_required
def profile():
    """الملف الشخصي"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """تغيير كلمة المرور"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('كلمة المرور الحالية غير صحيحة.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('تم تغيير كلمة المرور بنجاح.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """إعادة تعيين كلمة مرور المستخدم"""
    user = User.query.get_or_404(user_id)
    
    # كلمة مرور مؤقتة
    temp_password = f"temp{user.id}123"
    user.set_password(temp_password)
    db.session.commit()
    
    flash(f'تم إعادة تعيين كلمة مرور المستخدم {user.username}. كلمة المرور المؤقتة: {temp_password}', 'info')
    return redirect(url_for('auth.users_list'))

@auth_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """تفعيل/إلغاء تفعيل المستخدم"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('لا يمكنك تعديل حالة حسابك الخاص.', 'error')
        return redirect(url_for('auth.users_list'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'تم تفعيل' if user.is_active else 'تم إلغاء تفعيل'
    flash(f'{status} المستخدم {user.username}.', 'success')
    
    return redirect(url_for('auth.users_list'))

def init_default_users():
    """إنشاء المستخدمين الافتراضيين"""
    # التحقق من وجود مدير
    admin = User.query.filter_by(role=UserRole.ADMIN).first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@tax.com',
            role=UserRole.ADMIN,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    # إنشاء محاسب افتراضي
    accountant = User.query.filter_by(email='accountant@tax.com').first()
    if not accountant:
        accountant = User(
            username='accountant',
            email='accountant@tax.com',
            role=UserRole.ACCOUNTANT,
            is_active=True
        )
        accountant.set_password('acc123')
        db.session.add(accountant)
    
    db.session.commit()

def get_user_permissions(user):
    """الحصول على قائمة صلاحيات المستخدم"""
    if not user or not user.is_authenticated:
        return []
    
    permissions_map = {
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
    
    return permissions_map.get(user.role, [])
