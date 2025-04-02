from django.apps import AppConfig

class CompaniesManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'companies_manager'

    def ready(self):
        # تأكد من تحميل الإشارات فقط بعد تحميل جميع النماذج
        from django.contrib.auth import get_user_model
        User = get_user_model()
        import companies_manager.signals