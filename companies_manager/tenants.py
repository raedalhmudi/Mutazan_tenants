from django_tenants.signals import post_schema_sync
from django.db import connection

def create_tenant_tables(sender, **kwargs):
    tenant = kwargs.get('tenant')
    
    with connection.cursor() as cursor:
        # إنشاء جدول ملف المستخدم في كل tenant
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {tenant.schema_name}.companies_manager_userprofile (
                id serial PRIMARY KEY,
                user_id integer NOT NULL REFERENCES {tenant.schema_name}.auth_user (id) DEFERRABLE INITIALLY DEFERRED,
                phone_number varchar(15) NULL,
                address text NULL,
                profile_picture varchar(100) NULL
            )
        """)

post_schema_sync.connect(create_tenant_tables)