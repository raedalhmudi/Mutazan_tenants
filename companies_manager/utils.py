from django_tenants.utils import schema_context
from companies_manager.models import Company, WeightCardMain
from system_companies.models import WeightCard, ViolationRecord, Entry_and_exit

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

def transfer_entry_and_exit():
    companies = Company.objects.all()
    for company in companies:
        schema_name = company.schema_name
        with schema_context(schema_name):
            entry_and_exits = Entry_and_exit.objects.all()
            for entry_and_exit in entry_and_exits:
                print(f"{schema_name} | {entry_and_exit.plate_number_E_e.plate_number} | {entry_and_exit.entry_date}")
