# دليل النشر السريع على Railway

## 📋 قائمة التحقق قبل النشر

- ✅ تم إنشاء جميع الملفات المطلوبة
- ✅ تم تحديث معلومات التواصل
- ✅ تم تكوين قاعدة البيانات للإنتاج
- ✅ تم إضافة متطلبات الإنتاج

## 🚀 خطوات النشر

### 1. رفع المشروع على GitHub

```bash
# في مجلد المشروع
git init
git add .
git commit -m "Initial commit - Tax Declaration System by Mr-TITO"
git branch -M main

# استبدل YOUR_USERNAME باسم المستخدم الخاص بك على GitHub
git remote add origin https://github.com/YOUR_USERNAME/TaxDeclarationSystem.git
git push -u origin main
```

### 2. النشر على Railway

1. **إنشاء حساب على Railway**
   - اذهب إلى [railway.app](https://railway.app)
   - سجل دخول باستخدام GitHub

2. **إنشاء مشروع جديد**
   - اضغط على "New Project"
   - اختر "Deploy from GitHub repo"
   - اختر مستودع `TaxDeclarationSystem`

3. **إضافة قاعدة بيانات PostgreSQL**
   - في لوحة تحكم المشروع، اضغط على "New"
   - اختر "Database" ثم "PostgreSQL"
   - سيتم إنشاء قاعدة البيانات وربطها تلقائياً

4. **إعداد متغيرات البيئة**
   - اذهب إلى تبويب "Variables"
   - أضف المتغيرات التالية:

   ```
   SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
   FLASK_ENV=production
   ```

   > **ملاحظة**: `DATABASE_URL` سيتم إضافته تلقائياً عند ربط PostgreSQL

### 3. التحقق من النشر

1. انتظر حتى يكتمل البناء (Build)
2. اضغط على رابط التطبيق المُنشأ
3. يجب أن تظهر صفحة تسجيل الدخول
4. جرب تسجيل الدخول بالبيانات الافتراضية:
   - **المدير**: admin@tax.com / admin123
   - **محاسب**: accountant@tax.com / acc123

## 🔧 استكشاف الأخطاء

### مشكلة في البناء (Build Failed)
- تحقق من ملف `requirements.txt`
- تأكد من وجود `runtime.txt` مع إصدار Python صحيح

### مشكلة في قاعدة البيانات
- تأكد من إضافة PostgreSQL للمشروع
- تحقق من متغير `DATABASE_URL` في Variables

### مشكلة في التطبيق (Application Error)
- تحقق من Logs في Railway
- تأكد من إعداد `SECRET_KEY` في Variables

## 📱 بعد النشر

1. **تخصيص الدومين** (اختياري)
   - يمكنك ربط دومين مخصص من إعدادات Railway

2. **مراقبة الأداء**
   - استخدم لوحة تحكم Railway لمراقبة الاستخدام

3. **النسخ الاحتياطي**
   - Railway يوفر نسخ احتياطية تلقائية لقاعدة البيانات

## 🆘 الدعم

إذا واجهت أي مشاكل:

- 📱 واتساب: [+201028893818](https://wa.me/+201028893818)
- 📘 فيسبوك: [ahmed.ayman.871106](https://www.facebook.com/ahmed.ayman.871106)
- 📧 تليجرام: [@mrtito](https://t.me/mrtito)

---

**Created By Mr-TITO** 🚀
