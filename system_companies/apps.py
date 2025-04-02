from django.apps import AppConfig


class SystemCompaniesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'system_companies'

    def ready(self):
        import system_companies.signals 
