from app.models import FreightDocument


data = {
    "carrier_name": "Apex Logistics Solutions LLC",
    "load_number": "LD-994821",
    "pickup_location": {
        "city": "Dallas",
        "state": "TX",
        "zip": "75201"
    },
    "delivery_location": {
        "city": "Atlanta",
        "state": "GA",
        "zip": "30303"
    },
    "total_linehaul_rate": 2200.0,
    "fuel_surcharge": 350.0,
    "total_pay": 2800.0,
    "weight_lbs": 46800
}


document = FreightDocument(**data)

print(document)
print("\nJSON:")
print(document.model_dump_json(indent=2))