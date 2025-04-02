from django_tenants.utils import schema_context
from companies_manager.models import Company, WeightCardMain
from system_companies.models import WeightCard  # جدول بطاقات الوزن من نظام الشركات

def transfer_weight_cards():
    """نقل بطاقات الوزن من جميع الشركات إلى النظام الرئيسي"""
    companies = Company.objects.all()  # جلب جميع الشركات

    for company in companies:
        schema_name = company.schema_name  # جلب اسم Schema الخاص بالشركة

        with schema_context(schema_name):  # التبديل إلى Schema الشركة
            weight_cards = WeightCard.objects.all()  # جلب جميع بطاقات الوزن
            
            # إنشاء نسخ جديدة من البطاقات داخل النظام الرئيسي
            for card in weight_cards:
                # التحقق مما إذا كانت البطاقة موجودة مسبقًا في النظام الرئيسي
                if not WeightCardMain.objects.filter(
                    schema_name=schema_name,
                    plate_number=card.plate_number.plate_number,
                    entry_date=card.entry_date,
                    exit_date=card.exit_date
                ).exists():
                    WeightCardMain.objects.create(
                        schema_name=schema_name,
                        plate_number=card.plate_number.plate_number,  # جلب رقم الشاحنة
                        empty_weight=card.empty_weight,
                        loaded_weight=card.loaded_weight,
                        net_weight=card.net_weight,
                        driver_name=card.driver_name.driver_name if card.driver_name else None,
                        entry_date=card.entry_date,
                        exit_date=card.exit_date,
                        quantity=card.quantity,
                        material=card.material.name_material if card.material else None,
                        status=card.status,
                    )
        print(f"✅ تم نقل بطاقات الوزن من الشركة: {company.company_name} ({schema_name})")
