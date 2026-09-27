from pydantic import BaseModel


class Location(BaseModel):
    city: str
    state: str
    zip: str


class FreightDocument(BaseModel):
    carrier_name: str
    load_number: str
    pickup_location: Location
    delivery_location: Location
    total_linehaul_rate: float
    fuel_surcharge: float
    total_pay: float
    weight_lbs: int