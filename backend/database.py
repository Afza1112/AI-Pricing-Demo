from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
from datetime import datetime, timedelta
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./pricing_demo.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_data(db):
    """Seed database with demo data"""
    
    # Check if data already exists
    if db.query(models.Material).first():
        return
    
    # Materials
    materials_data = [
        {"name": "Concrete C30/37", "unit": "m³", "category": "Concrete", "spec": "Standard structural concrete", "mapping_key": "concrete_c30"},
        {"name": "Steel Rebar B500C", "unit": "kg", "category": "Steel", "spec": "High-yield deformed bars", "mapping_key": "rebar_b500c"},
        {"name": "Structural Steel S355", "unit": "kg", "category": "Steel", "spec": "Hot-rolled structural steel", "mapping_key": "steel_s355"},
        {"name": "Cement CEM I 42.5", "unit": "t", "category": "Cement", "spec": "Portland cement", "mapping_key": "cement_42_5"},
        {"name": "Bitumen 50/70", "unit": "t", "category": "Bitumen", "spec": "Road construction bitumen", "mapping_key": "bitumen_50_70"},
        {"name": "Aggregate 0-32mm", "unit": "t", "category": "Aggregate", "spec": "Mixed aggregate", "mapping_key": "aggregate_mixed"},
        {"name": "Formwork Plywood", "unit": "m²", "category": "Formwork", "spec": "18mm marine plywood", "mapping_key": "formwork_plywood"},
        {"name": "Labor - Skilled", "unit": "hour", "category": "Labor", "spec": "Skilled construction worker", "mapping_key": "labor_skilled"},
        {"name": "Labor - General", "unit": "hour", "category": "Labor", "spec": "General construction worker", "mapping_key": "labor_general"},
        {"name": "Excavator Rental", "unit": "day", "category": "Equipment", "spec": "20-ton excavator", "mapping_key": "excavator_20t"}
    ]
    
    for mat_data in materials_data:
        material = models.Material(**mat_data)
        db.add(material)
    
    db.commit()
    
    # Price indices (last 24 months)
    base_date = datetime.now() - timedelta(days=730)
    materials = db.query(models.Material).all()
    
    base_prices = {
        "concrete_c30": 85.0,
        "rebar_b500c": 0.75,
        "steel_s355": 1.20,
        "cement_42_5": 120.0,
        "bitumen_50_70": 450.0,
        "aggregate_mixed": 25.0,
        "formwork_plywood": 35.0,
        "labor_skilled": 25.0,
        "labor_general": 18.0,
        "excavator_20t": 350.0
    }
    
    for material in materials:
        base_price = base_prices.get(material.mapping_key, 100.0)
        
        # Generate 24 months of price data with trends
        for i in range(24):
            date = base_date + timedelta(days=i*30)
            # Add some price variation (±15%)
            price_variation = 1.0 + (i % 12 - 6) * 0.025  # Seasonal variation
            price = base_price * price_variation
            
            price_index = models.PriceIndex(
                material_id=material.id,
                region="Greece",
                date=date,
                unit_price=price
            )
            db.add(price_index)
    
    # Seasonality factors
    seasonal_patterns = {
        "concrete_c30": [1.05, 1.03, 1.00, 0.98, 0.95, 0.93, 0.95, 0.97, 1.00, 1.02, 1.05, 1.08],
        "rebar_b500c": [1.08, 1.05, 1.02, 0.98, 0.95, 0.92, 0.95, 0.98, 1.02, 1.05, 1.08, 1.10],
        "steel_s355": [1.10, 1.07, 1.03, 0.98, 0.94, 0.90, 0.93, 0.97, 1.02, 1.06, 1.10, 1.12],
        "cement_42_5": [1.03, 1.02, 1.00, 0.99, 0.97, 0.95, 0.97, 0.99, 1.01, 1.02, 1.03, 1.04],
        "bitumen_50_70": [1.15, 1.10, 1.05, 0.95, 0.85, 0.80, 0.85, 0.95, 1.05, 1.10, 1.15, 1.20],
        "aggregate_mixed": [1.02, 1.01, 1.00, 0.99, 0.98, 0.97, 0.98, 0.99, 1.00, 1.01, 1.02, 1.03],
        "formwork_plywood": [1.05, 1.03, 1.01, 0.99, 0.97, 0.95, 0.97, 0.99, 1.01, 1.03, 1.05, 1.07],
        "labor_skilled": [1.00, 1.00, 1.02, 1.05, 1.08, 1.10, 1.08, 1.05, 1.02, 1.00, 1.00, 1.00],
        "labor_general": [1.00, 1.00, 1.02, 1.05, 1.08, 1.10, 1.08, 1.05, 1.02, 1.00, 1.00, 1.00],
        "excavator_20t": [1.10, 1.08, 1.05, 1.02, 0.98, 0.95, 0.98, 1.02, 1.05, 1.08, 1.10, 1.12]
    }
    
    for material in materials:
        factors = seasonal_patterns.get(material.mapping_key, [1.0] * 12)
        for month, factor in enumerate(factors, 1):
            seasonality = models.Seasonality(
                material_id=material.id,
                month=month,
                factor=factor
            )
            db.add(seasonality)
    
    # Vendors
    vendors_data = [
        {
            "name": "Hellenic Concrete Co.",
            "region": "Athens",
            "contacts": {"email": "sales@hellenic-concrete.gr", "phone": "+30 210 123 4567"},
            "reliability_score": 4.5
        },
        {
            "name": "Steel Masters SA",
            "region": "Thessaloniki",
            "contacts": {"email": "orders@steelmasters.gr", "phone": "+30 231 987 6543"},
            "reliability_score": 4.2
        },
        {
            "name": "Mediterranean Aggregates",
            "region": "Patras",
            "contacts": {"email": "info@med-aggregates.gr", "phone": "+30 261 555 0123"},
            "reliability_score": 4.0
        },
        {
            "name": "Athens Construction Supply",
            "region": "Athens",
            "contacts": {"email": "supply@athens-construction.gr", "phone": "+30 210 888 9999"},
            "reliability_score": 4.3
        },
        {
            "name": "Northern Equipment Rental",
            "region": "Thessaloniki",
            "contacts": {"email": "rentals@northern-equip.gr", "phone": "+30 231 444 5555"},
            "reliability_score": 4.1
        }
    ]
    
    for vendor_data in vendors_data:
        vendor = models.Vendor(**vendor_data)
        db.add(vendor)
    
    db.commit()
    
    # Vendor offers
    vendors = db.query(models.Vendor).all()
    
    vendor_offers_data = [
        # Hellenic Concrete Co.
        {"vendor_id": 1, "material_id": 1, "unit_price": 82.0, "stock_qty": 1000, "lead_time_days": 3, "moq": 10},
        {"vendor_id": 1, "material_id": 4, "unit_price": 115.0, "stock_qty": 500, "lead_time_days": 7, "moq": 5},
        
        # Steel Masters SA
        {"vendor_id": 2, "material_id": 2, "unit_price": 0.72, "stock_qty": 50000, "lead_time_days": 14, "moq": 1000},
        {"vendor_id": 2, "material_id": 3, "unit_price": 1.15, "stock_qty": 25000, "lead_time_days": 21, "moq": 500},
        
        # Mediterranean Aggregates
        {"vendor_id": 3, "material_id": 6, "unit_price": 23.0, "stock_qty": 2000, "lead_time_days": 2, "moq": 20},
        {"vendor_id": 3, "material_id": 5, "unit_price": 440.0, "stock_qty": 100, "lead_time_days": 10, "moq": 2},
        
        # Athens Construction Supply
        {"vendor_id": 4, "material_id": 7, "unit_price": 33.0, "stock_qty": 800, "lead_time_days": 5, "moq": 50},
        {"vendor_id": 4, "material_id": 8, "unit_price": 24.0, "stock_qty": 0, "lead_time_days": 1, "moq": 8},
        
        # Northern Equipment Rental
        {"vendor_id": 5, "material_id": 10, "unit_price": 340.0, "stock_qty": 5, "lead_time_days": 1, "moq": 1},
        {"vendor_id": 5, "material_id": 9, "unit_price": 17.0, "stock_qty": 0, "lead_time_days": 1, "moq": 8}
    ]
    
    for offer_data in vendor_offers_data:
        offer = models.VendorOffer(**offer_data, tier_rules={})
        db.add(offer)
    
    db.commit()
    print("Database seeded with demo data")