from main import execute_workflow


def test_flagged_document():
    text = """
    FREIGHT RATE CONFIRMATION

    Ref #: LD-994821
    Carrier: Apex Logistics Solutions LLC

    PICKUP DETAILS:
    Origin: Distribution Center 4, Dallas, TX 75201

    DROP-OFF DETAILS:
    Destination: Warehouse B, Atlanta, GA 30303

    CARGO DETAILS:
    Description: Industrial Machinery Parts
    Total Weight: 46,800 lbs (Gross)

    FINANCIAL AGREEMENT:
    Linehaul Rate: $2,200.00
    Fuel Surcharge (FSC): $350.00
    Total Agreed Amount: $2,800.00
    """

    result = execute_workflow(text)

    assert result["status"] == "FLAGGED_FOR_HUMAN_REVIEW"
    assert "RATE_MISMATCH" in result["flag_reasons"]
    assert "OVERWEIGHT_LOAD" in result["flag_reasons"]

    print("✅ End-to-end flagged document test passed")


if __name__ == "__main__":
    test_flagged_document()
    print("\n🎉 End-to-end test passed!")