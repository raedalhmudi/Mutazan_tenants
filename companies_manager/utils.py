from django_tenants.utils import schema_context
from companies_manager.models import Company, WeightCardMain
from system_companies.models import WeightCard, ViolationRecord

def transfer_weight_cards():
    companies = Company.objects.all()
    for company in companies:
        schema_name = company.schema_name
        with schema_context(schema_name):
            weight_cards = WeightCard.objects.all()
            for card in weight_cards:
                existing_card = WeightCardMain.objects.filter(
                    schema_name=schema_name,
                    plate_number=card.plate_number.plate_number,
                    entry_date=card.entry_date
                ).first()

                if existing_card:
                    if existing_card.status != "complete":
                        existing_card.status = card.status
                        existing_card.exit_date = card.exit_date
                        existing_card.loaded_weight = card.loaded_weight
                        existing_card.net_weight = card.net_weight
                        existing_card.quantity = card.quantity
                        existing_card.save()
                else:
                    WeightCardMain.objects.create(
                        schema_name=schema_name,
                        plate_number=card.plate_number.plate_number,
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

def transfer_violations():
    companies = Company.objects.all()
    for company in companies:
        schema_name = company.schema_name
        with schema_context(schema_name):
            violations = ViolationRecord.objects.all()
            for violation in violations:
                existing_violation = WeightCardMain.objects.filter(
                    schema_name=schema_name,
                    plate_number=violation.plate_number_vio.plate_number,
                    timestamp=violation.timestamp,
                    violation_type=violation.violation_type.name if violation.violation_type else None
                ).exists()

                if not existing_violation:
                    WeightCardMain.objects.create(
                        schema_name=schema_name,
                        plate_number=violation.plate_number_vio.plate_number,
                        violation_type=violation.violation_type.name if violation.violation_type else None,
                        timestamp=violation.timestamp,
                        device_vio=violation.device_vio.name if violation.device_vio else None,
                        entry_exit_log=str(violation.entry_exit_log) if violation.entry_exit_log else None,
                        weight_card_vio=str(violation.weight_card_vio) if violation.weight_card_vio else None,
                        status='complete'
                    )