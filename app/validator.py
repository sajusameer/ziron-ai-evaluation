from app.models import FreightDocument


def validate_freight_document(
    document: FreightDocument,
) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []

    # 1. Financial validation
    expected_total = (
        document.total_linehaul_rate
        + document.fuel_surcharge
    )

    if expected_total != document.total_pay:
        errors.append("RATE_MISMATCH")

    # 2. Weight validation
    if document.weight_lbs > 45_000:
        warnings.append("OVERWEIGHT_LOAD")

    # 3. Required field validation
    if not document.load_number.strip():
        errors.append("INCOMPLETE_DATA")

    if not document.pickup_location.city.strip():
        errors.append("INCOMPLETE_DATA")

    if not document.delivery_location.city.strip():
        errors.append("INCOMPLETE_DATA")

    return errors, warnings