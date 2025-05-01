#------------الكود حق رائد-------------
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction

@receiver(post_save, sender=User)
def encrypt_password_on_create(sender, instance, created, **kwargs):
    if created:
        raw_password = instance.password
        # ✅ نتأكد إن كلمة السر مش مشفرة
        if not raw_password.startswith('pbkdf2_sha256$'):
            instance.password = make_password(raw_password)
            # نستخدم transaction.on_commit عشان ما يصير save داخل save
            transaction.on_commit(lambda: instance.save())



#---------------الحل حق عصام-------------------


# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from django.contrib.auth.hashers import make_password
# from django.db import transaction, connection
# from .models import Company  # استيراد نموذج الشركة الخاص بك

# @receiver(post_save, sender=User)
# def encrypt_password_on_create(sender, instance, created, **kwargs):
#     if created:
#         raw_password = instance.password
#         if not raw_password.startswith('pbkdf2_sha256$'):
#             instance.password = make_password(raw_password)
#             transaction.on_commit(lambda: instance.save())

# @receiver(post_save, sender=Company)
# def create_company_schema(sender, instance, created, **kwargs):
#     if created:
#         schema_name = f"company_{instance.id}"  # تسمية Schema بناءً على ID الشركة
        
#         try:
#             with connection.cursor() as cursor:
#                 # 1. إنشاء Schema جديد
#                 cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                
#                 # 2. منح الصلاحيات للمستخدم الحالي
#                 cursor.execute(f"GRANT ALL ON SCHEMA {schema_name} TO CURRENT_USER")
                
#                 # 3. نسخ الجداول الأساسية من public إلى Schema الشركة
#                 cursor.execute("""
#                     SELECT table_name 
#                     FROM information_schema.tables 
#                     WHERE table_schema = 'public'
#                     AND table_type = 'BASE TABLE'
#                 """)
#                 tables = [row[0] for row in cursor.fetchall()]
                
#                 for table in tables:
#                     # نسخ الهيكل مع البيانات
#                     cursor.execute(f"""
#                         CREATE TABLE {schema_name}.{table} 
#                         AS TABLE public.{table} WITH DATA
#                     """)
                
#                 # 4. تحديث نموذج الشركة بحفظ اسم Schema
#                 instance.schema_name = schema_name
#                 instance.save()
                
#         except Exception as e:
#             print(f"فشل إنشاء Schema: {e}")
#             # يمكنك إضافة آلية لمعالجة الأخطاء هنا