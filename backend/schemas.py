from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class EstimateRequest(BaseModel):
    project_type: str  # "bridge", "hotel", "business_park"
    location: str
    size: float
    size_unit: str  # "m2", "lane_km", "rooms"
    start_month: int
    duration_months: int
    
    # Optional detailed inputs
    structural_class: Optional[str] = None
    star_rating: Optional[int] = None
    storey_count: Optional[int] = None
    facade_type: Optional[str] = None
    concrete_class: Optional[str] = None
    rebar_grade: Optional[str] = None
    earthworks_volume: Optional[float] = None
    preferred_vendors: Optional[List[str]] = None

class BoQItem(BaseModel):
    material_name: str
    quantity: float
    unit: str
    unit_price: float
    total_price: float
    seasonal_factor: float
    confidence_band: Dict[str, float]  # P25, P50, P75

class VendorRecommendation(BaseModel):
    vendor_name: str
    location: str
    price: float
    stock_status: str
    lead_time_days: int
    moq: float
    contact: str

class EstimateResponse(BaseModel):
    id: str
    boq_items: List[BoQItem]
    total_cost: float
    confidence_bands: Dict[str, float]
    vendor_recommendations: Dict[str, List[VendorRecommendation]]
    seasonal_chart_data: List[Dict[str, Any]]
    assumptions: List[str]
    cost_drivers: List[Dict[str, Any]]

class MaterialResponse(BaseModel):
    id: int
    name: str
    unit: str
    category: str
    spec: str
    
    class Config:
        from_attributes = True

class VendorResponse(BaseModel):
    id: int
    name: str
    region: str
    contacts: Dict[str, Any]
    reliability_score: float
    
    class Config:
        from_attributes = True