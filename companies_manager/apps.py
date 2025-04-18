from django.apps import AppConfig

class CompaniesManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'companies_manager'

    def ready(self):
        import companies_manager.signals  # استدعاء الإشارات
