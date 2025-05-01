from django_tenants.utils import schema_context
from companies_manager.models import Company, WeightCardMain
from system_companies.models import WeightCard, ViolationRecord, Trucks

def transfer_weight_cards():
    companies = Company.objects.all()
    for company in companies:
        schema_name = company.schema_name
        with schema_context(schema_name):
            weight_cards = WeightCard.objects.all()
            for card in weight_cards:
                print(f"{schema_name} | {card.plate_number.plate_number} | {card.entry_date} | {card.status}")


def transfer_violations():
    companies = Company.objects.all()
    for company in companies:
        schema_name = company.schema_name
        with schema_context(schema_name):
            violations = ViolationRecord.objects.all()
            for violation in violations:
                print(f"{schema_name} | {violation.plate_number_vio.plate_number} | {violation.timestamp}")

# def transfer_trucks():
#     companies = Company.objects.all()
#     for company in companies:
#         schema_name = company.schema_name
#         with schema_context(schema_name):
#             trucks = Trucks.objects.all()
#             for truck in trucks:
#                 print(f"{schema_name} | {truck.plate_number_vio.plate_number} | {truck.timestamp}")
