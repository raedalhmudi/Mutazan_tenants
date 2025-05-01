from django.contrib import admin
from django.utils.html import format_html

class BaseAdmin(admin.ModelAdmin):
    """
    كلاس أساسي مخصص لإدارة النماذج في واجهة الأدمن يحتوي على:
    1. فلترة الـ ForeignKey حسب condition=True
    2. تنسيقات مشتركة للجداول والأزرار
    3. دالة لعرض أزرار الحالة
    """
    
    # إعدادات الجداول المشتركة
    list_per_page = 25
    list_max_show_all = 100
    save_on_top = True

    # فلترة الـ ForeignKey
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """فلترة العلاقات الخارجية حسب condition=True"""
        related_model = db_field.related_model
        
        if related_model and hasattr(related_model, 'condition'):
            kwargs["queryset"] = related_model.objects.filter(condition=True)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # دالة أزرار الحالة
    def status_badge(self, obj):
        """عرض الحالة كزر بلون مميز"""
        if obj.status == "completed":
            css_class = "status-completed"
            status_text = "مكتمل"
        elif obj.status == "processing":
            css_class = "status-processing"
            status_text = "قيد المعالجة"
        else:  # pending or other
            css_class = "status-pending"
            status_text = "معلق"
        
        return format_html(
            f'<span class="status-badge {css_class}">{status_text}</span>'
        )
    status_badge.short_description = "الحالة"

    # تنسيقات CSS وJS المخصصة
    class Media:
        css = {
            'all': ('common/css/system_companies/custom.css',)
        }
        js = ('common/js/system_companies/custom.js',)  # إذا كان لديك ملف JS