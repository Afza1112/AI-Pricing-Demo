from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    unit = Column(String)
    category = Column(String)
    spec = Column(Text)
    mapping_key = Column(String, index=True)
    
    price_indices = relationship("PriceIndex", back_populates="material")
    seasonality = relationship("Seasonality", back_populates="material")

class PriceIndex(Base):
    __tablename__ = "price_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"))
    region = Column(String)
    date = Column(DateTime)
    unit_price = Column(Float)
    
    material = relationship("Material", back_populates="price_indices")

class Seasonality(Base):
    __tablename__ = "seasonality"
    
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"))
    month = Column(Integer)
    factor = Column(Float)
    
    material = relationship("Material", back_populates="seasonality")

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    region = Column(String)
    contacts = Column(JSON)
    reliability_score = Column(Float)
    
    offers = relationship("VendorOffer", back_populates="vendor")

class VendorOffer(Base):
    __tablename__ = "vendor_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    unit_price = Column(Float)
    stock_qty = Column(Float)
    lead_time_days = Column(Integer)
    moq = Column(Float)
    tier_rules = Column(JSON)
    
    vendor = relationship("Vendor", back_populates="offers")
    material = relationship("Material")

class Estimate(Base):
    __tablename__ = "estimates"
    
    id = Column(String, primary_key=True, index=True)
    project_meta = Column(JSON)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)