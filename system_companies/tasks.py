# from celery import shared_task
# from django_tenants.utils import schema_context
# from system_companies.models import WeightCard
# from companies_manager.models import WeightCardLog

# @shared_task
# def transfer_weight_card_to_main(weight_card_id, company_schema):
#     """
#     تنقل بطاقة الوزن من قاعدة بيانات الشركة إلى قاعدة بيانات النظام الرئيسي
#     """
#     with schema_context(company_schema):  # التبديل إلى قاعدة بيانات الشركة
#         try:
#             weight_card = WeightCard.objects.get(id=weight_card_id)

#             # التحقق مما إذا كانت البطاقة موجودة بالفعل في النظام الرئيسي
#             if WeightCardLog.objects.filter(weight_card_id=weight_card.id).exists():
#                 return f"بطاقة الوزن {weight_card.id} موجودة بالفعل."

#             # إدخال البيانات في قاعدة بيانات النظام الرئيسي
#             WeightCardLog.objects.create(
#                 weight_card_id=weight_card.id,
#                 company_id=weight_card.company.id,
#                 plate_number=weight_card.plate_number.plate_number,
#                 empty_weight=weight_card.empty_weight,
#                 loaded_weight=weight_card.loaded_weight,
#                 net_weight=weight_card.net_weight,
#                 driver_name=weight_card.driver_name.name if weight_card.driver_name else None,
#                 entry_date=weight_card.entry_date,
#                 exit_date=weight_card.exit_date,
#                 quantity=weight_card.quantity,
#                 material=weight_card.material.name if weight_card.material else None,
#                 status=weight_card.status,
#             )

#             return f"تم نقل بطاقة الوزن {weight_card.id} بنجاح."
#         except WeightCard.DoesNotExist:
#             return f"بطاقة الوزن {weight_card_id} غير موجودة."
