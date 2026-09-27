from app.models import FreightDocument, Location
from app.validator import validate_freight_document


def create_document(
    total_pay: float = 2550.0,
    weight_lbs: int = 40_000,
    load_number: str = "LD-994821",
) -> FreightDocument:
    return FreightDocument(
        carrier_name="Apex Logistics Solutions LLC",
        load_number=load_number,
        pickup_location=Location(
            city="Dallas",
            state="TX",
            zip="75201",
        ),
        delivery_location=Location(
            city="Atlanta",
            state="GA",
            zip="30303",
        ),
        total_linehaul_rate=2200.0,
        fuel_surcharge=350.0,
        total_pay=total_pay,
        weight_lbs=weight_lbs,
    )


def test_valid_document():
    document = create_document()

    errors, warnings = validate_freight_document(document)

    assert errors == []
    assert warnings == []

    print("✅ Valid document test passed")


def test_rate_mismatch():
    document = create_document(total_pay=2800.0)

    errors, warnings = validate_freight_document(document)

    assert "RATE_MISMATCH" in errors
    assert warnings == []

    print("✅ Rate mismatch test passed")


def test_overweight_load():
    document = create_document(weight_lbs=46_800)

    errors, warnings = validate_freight_document(document)

    assert errors == []
    assert "OVERWEIGHT_LOAD" in warnings

    print("✅ Overweight load test passed")


def test_incomplete_data():
    document = create_document(load_number="")

    errors, warnings = validate_freight_document(document)

    assert "INCOMPLETE_DATA" in errors

    print("✅ Incomplete data test passed")


if __name__ == "__main__":
    test_valid_document()
    test_rate_mismatch()
    test_overweight_load()
    test_incomplete_data()

    print("\n🎉 All validation tests passed!")