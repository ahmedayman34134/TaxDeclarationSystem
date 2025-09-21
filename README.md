# نظام إدارة الإقرارات الضريبية
## Tax Declaration Management System

نظام متكامل لإدارة الإقرارات الضريبية يدعم الشركات والمؤسسات في إدارة ضرائبها بكفاءة.

## 🚀 المميزات الرئيسية

- ✅ **إدارة المنتجات** مع أنواع الضرائب المختلفة
- ✅ **حساب الضرائب التلقائي** (ضريبة القيمة المضافة 14% - ضريبة الخصم والإضافة 5%)
- ✅ **نظام الفواتير المتطور** مع إنشاء PDF
- ✅ **تقارير ضريبية شاملة** قابلة للتصدير
- ✅ **نظام المستخدمين والصلاحيات** متعدد المستويات
- ✅ **النسخ الاحتياطي واستعادة البيانات** التلقائي
- ✅ **واجهة مستخدم جميلة ومتجاوبة** تدعم العربية
- ✅ **دعم قواعد البيانات المتعددة** (SQLite, PostgreSQL)

## 🛠️ التقنيات المستخدمة

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: Bootstrap 5, JavaScript, Font Awesome
- **Database**: SQLite (تطوير) / PostgreSQL (إنتاج)
- **PDF Generation**: ReportLab
- **Authentication**: Flask-Login
- **Forms**: WTForms, Flask-WTF

## 📋 متطلبات التشغيل

- Python 3.8+
- pip (Python package manager)

## 🚀 التشغيل المحلي

### 1. استنساخ المشروع
```bash
git clone https://github.com/yourusername/TaxDeclarationSystem.git
cd TaxDeclarationSystem
```

### 2. إنشاء بيئة افتراضية
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. إعداد متغيرات البيئة
```bash
cp .env.example .env
# قم بتحرير ملف .env وإضافة القيم المطلوبة
```

### 5. تشغيل التطبيق
```bash
python app.py
```

### 6. فتح المتصفح
انتقل إلى: `http://localhost:5000`

## 🌐 النشر على Railway

### 1. رفع المشروع على GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/TaxDeclarationSystem.git
git push -u origin main
```

### 2. النشر على Railway
1. اذهب إلى [Railway.app](https://railway.app)
2. قم بتسجيل الدخول باستخدام GitHub
3. اضغط على "New Project"
4. اختر "Deploy from GitHub repo"
5. اختر مستودع المشروع
6. أضف متغيرات البيئة المطلوبة:
   - `SECRET_KEY`: مفتاح سري قوي
   - `FLASK_ENV`: production
   - `DATABASE_URL`: سيتم إضافته تلقائياً عند إضافة PostgreSQL

### 3. إضافة قاعدة بيانات PostgreSQL
1. في لوحة تحكم Railway، اضغط على "New"
2. اختر "Database" ثم "PostgreSQL"
3. سيتم ربط قاعدة البيانات تلقائياً

## 👥 بيانات الدخول الافتراضية

- **المدير**: admin@tax.com / admin123
- **محاسب**: accountant@tax.com / acc123

## 📁 هيكل المشروع

```
TaxDeclarationSystem/
├── app.py                 # التطبيق الرئيسي
├── models.py             # نماذج قاعدة البيانات
├── forms.py              # نماذج الويب
├── auth.py               # نظام المصادقة
├── reports.py            # نظام التقارير
├── backup.py             # نظام النسخ الاحتياطي
├── pdf_generator.py      # مولد ملفات PDF
├── requirements.txt      # متطلبات Python
├── Procfile             # تكوين Railway
├── railway.json         # إعدادات Railway
├── .env.example         # مثال على متغيرات البيئة
├── .gitignore          # ملفات مستبعدة من Git
├── templates/          # قوالب HTML
│   ├── auth/          # صفحات المصادقة
│   ├── reports/       # صفحات التقارير
│   ├── invoices/      # صفحات الفواتير
│   ├── products/      # صفحات المنتجات
│   ├── backup/        # صفحات النسخ الاحتياطي
│   └── errors/        # صفحات الأخطاء
├── static/            # الملفات الثابتة
│   ├── css/          # ملفات CSS
│   ├── js/           # ملفات JavaScript
│   └── images/       # الصور
└── instance/         # قاعدة البيانات والملفات المحلية
```

## 🔧 المتغيرات البيئية

| المتغير | الوصف | مطلوب |
|---------|--------|--------|
| `SECRET_KEY` | مفتاح سري للتشفير | ✅ |
| `DATABASE_URL` | رابط قاعدة البيانات | ✅ |
| `FLASK_ENV` | بيئة التشغيل (development/production) | ✅ |
| `PORT` | رقم البورت (يتم تعيينه تلقائياً في Railway) | ❌ |

## 📊 لقطات الشاشة

### لوحة التحكم
![Dashboard](screenshots/dashboard.png)

### إدارة الفواتير
![Invoices](screenshots/invoices.png)

### التقارير الضريبية
![Reports](screenshots/reports.png)

## 🤝 المساهمة

نرحب بالمساهمات! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى الفرع (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

## 📝 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 👨‍💻 المطور

**Created By Mr-TITO**

- 📱 واتساب: [+201028893818](https://wa.me/+201028893818)
- 📘 فيسبوك: [ahmed.ayman.871106](https://www.facebook.com/ahmed.ayman.871106)
- 📧 تليجرام: [@mrtito](https://t.me/mrtito)

## 🆘 الدعم الفني

للحصول على الدعم الفني أو الإبلاغ عن مشاكل:

1. افتح [Issue جديد](https://github.com/yourusername/TaxDeclarationSystem/issues)
2. تواصل معنا عبر وسائل التواصل المذكورة أعلاه
3. راسلنا على البريد الإلكتروني

---

⭐ إذا أعجبك هذا المشروع، لا تنس إعطاؤه نجمة على GitHub!
