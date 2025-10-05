import models
import schemas
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
import csv

# Project templates with parametric models
PROJECT_TEMPLATES = {
    "bridge": {
        "concrete_c30": lambda size: size * 0.8,  # m³ per lane-km
        "rebar_b500c": lambda size: size * 120,   # kg per lane-km
        "steel_s355": lambda size: size * 80,     # kg per lane-km
        "formwork_plywood": lambda size: size * 15, # m² per lane-km
        "labor_skilled": lambda size: size * 200,  # hours per lane-km
        "labor_general": lambda size: size * 300,  # hours per lane-km
        "excavator_20t": lambda size: size * 10    # days per lane-km
    },
    "hotel": {
        "concrete_c30": lambda size: size * 0.3,  # m³ per room
        "rebar_b500c": lambda size: size * 45,    # kg per room
        "steel_s355": lambda size: size * 25,     # kg per room
        "formwork_plywood": lambda size: size * 8, # m² per room
        "labor_skilled": lambda size: size * 80,   # hours per room
        "labor_general": lambda size: size * 120,  # hours per room
        "cement_42_5": lambda size: size * 0.15   # t per room
    },
    "business_park": {
        "concrete_c30": lambda size: size * 0.15, # m³ per m²
        "rebar_b500c": lambda size: size * 20,    # kg per m²
        "steel_s355": lambda size: size * 35,     # kg per m²
        "formwork_plywood": lambda size: size * 0.8, # m² per m²
        "labor_skilled": lambda size: size * 3,    # hours per m²
        "labor_general": lambda size: size * 5,    # hours per m²
        "aggregate_mixed": lambda size: size * 0.1 # t per m²
    }
}

def generate_estimate(request: schemas.EstimateRequest, db: Session):
    """Generate complete project estimate with BoQ, pricing, and vendor recommendations"""
    
    # Get project template
    template = PROJECT_TEMPLATES.get(request.project_type)
    if not template:
        raise ValueError(f"Unknown project type: {request.project_type}")
    
    # Generate BoQ
    boq_items = []
    vendor_recommendations = {}
    seasonal_chart_data = []
    assumptions = []
    cost_drivers = []
    
    total_cost = 0.0
    
    for material_key, quantity_func in template.items():
        # Get material
        material = db.query(models.Material).filter(
            models.Material.mapping_key == material_key
        ).first()
        
        if not material:
            continue
            
        # Calculate quantity
        quantity = quantity_func(request.size)
        
        # Get base price
        latest_price = db.query(models.PriceIndex).filter(
            models.PriceIndex.material_id == material.id,
            models.PriceIndex.region == "Greece"
        ).order_by(models.PriceIndex.date.desc()).first()
        
        if not latest_price:
            continue
            
        base_price = latest_price.unit_price
        
        # Apply seasonal factor
        seasonal_factor = db.query(models.Seasonality).filter(
            models.Seasonality.material_id == material.id,
            models.Seasonality.month == request.start_month
        ).first()
        
        seasonal_multiplier = seasonal_factor.factor if seasonal_factor else 1.0
        
        # Apply location factor (simplified)
        location_factor = 1.0
        if "athens" in request.location.lower():
            location_factor = 1.05
        elif "thessaloniki" in request.location.lower():
            location_factor = 0.98
        
        # Calculate final unit price
        unit_price = base_price * seasonal_multiplier * location_factor
        total_price = quantity * unit_price
        total_cost += total_price
        
        # Confidence bands (P25, P50, P75)
        confidence_band = {
            "P25": unit_price * 0.85,
            "P50": unit_price,
            "P75": unit_price * 1.15
        }
        
        # Create BoQ item as dict
        boq_item = {
            "material_name": material.name,
            "quantity": round(quantity, 2),
            "unit": material.unit,
            "unit_price": round(unit_price, 2),
            "total_price": round(total_price, 2),
            "seasonal_factor": round(seasonal_multiplier, 3),
            "confidence_band": confidence_band
        }
        boq_items.append(boq_item)
        
        # Get vendor recommendations
        vendors = db.query(models.VendorOffer).filter(
            models.VendorOffer.material_id == material.id
        ).join(models.Vendor).order_by(models.VendorOffer.unit_price).limit(3).all()
        
        vendor_recs = []
        for vendor_offer in vendors:
            stock_status = "In Stock" if vendor_offer.stock_qty >= quantity else "Limited Stock"
            if vendor_offer.stock_qty == 0:
                stock_status = "Out of Stock"
                
            vendor_rec = {
                "vendor_name": vendor_offer.vendor.name,
                "location": vendor_offer.vendor.region,
                "price": vendor_offer.unit_price,
                "stock_status": stock_status,
                "lead_time_days": vendor_offer.lead_time_days,
                "moq": vendor_offer.moq,
                "contact": vendor_offer.vendor.contacts.get("email", "N/A")
            }
            vendor_recs.append(vendor_rec)
        
        vendor_recommendations[material.name] = vendor_recs
        
        # Generate seasonal chart data
        seasonal_data = []
        for month in range(1, 13):
            seasonal_factor_month = db.query(models.Seasonality).filter(
                models.Seasonality.material_id == material.id,
                models.Seasonality.month == month
            ).first()
            
            factor = seasonal_factor_month.factor if seasonal_factor_month else 1.0
            seasonal_data.append({
                "month": month,
                "material": material.name,
                "price_factor": factor,
                "price": base_price * factor
            })
        
        seasonal_chart_data.extend(seasonal_data)
        
        # Add to cost drivers if significant
        if total_price > total_cost * 0.1:  # More than 10% of total cost
            cost_drivers.append({
                "material": material.name,
                "cost": total_price,
                "percentage": (total_price / total_cost) * 100
            })
    
    # Sort cost drivers by cost
    cost_drivers.sort(key=lambda x: x["cost"], reverse=True)
    cost_drivers = cost_drivers[:5]  # Top 5
    
    # Generate assumptions
    assumptions = [
        f"Project location: {request.location}",
        f"Start month: {request.start_month}",
        f"Duration: {request.duration_months} months",
        f"Size: {request.size} {request.size_unit}",
        "Prices based on latest market data",
        "Seasonal adjustments applied",
        "Regional factors included",
        "VAT not included"
    ]
    
    # Calculate confidence bands for total
    total_confidence_bands = {
        "P25": total_cost * 0.85,
        "P50": total_cost,
        "P75": total_cost * 1.15
    }
    
    return {
        "boq_items": boq_items,
        "total_cost": round(total_cost, 2),
        "confidence_bands": total_confidence_bands,
        "vendor_recommendations": vendor_recommendations,
        "seasonal_chart_data": seasonal_chart_data,
        "assumptions": assumptions,
        "cost_drivers": cost_drivers
    }

def generate_pdf_report(estimate: models.Estimate):
    """Generate PDF report for estimate"""
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/estimate_{estimate.id}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    story.append(Paragraph("AI Pricing & Sourcing Estimate", title_style))
    story.append(Spacer(1, 20))
    
    # Project details
    project_meta = estimate.project_meta
    story.append(Paragraph("Project Details", styles['Heading2']))
    
    project_data = [
        ["Project Type:", project_meta.get("project_type", "N/A").title()],
        ["Location:", project_meta.get("location", "N/A")],
        ["Size:", f"{project_meta.get('size', 'N/A')} {project_meta.get('size_unit', '')}"],
        ["Start Month:", str(project_meta.get("start_month", "N/A"))],
        ["Duration:", f"{project_meta.get('duration_months', 'N/A')} months"],
        ["Generated:", estimate.created_at.strftime("%Y-%m-%d %H:%M")]
    ]
    
    project_table = Table(project_data, colWidths=[2*inch, 3*inch])
    project_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(project_table)
    story.append(Spacer(1, 20))
    
    # Cost Summary
    results = estimate.results
    story.append(Paragraph("Cost Summary", styles['Heading2']))
    
    confidence_bands = results.get("confidence_bands", {})
    summary_data = [
        ["Estimate Level", "Cost (EUR)"],
        ["Optimistic (P25)", f"€{confidence_bands.get('P25', 0):,.2f}"],
        ["Most Likely (P50)", f"€{confidence_bands.get('P50', 0):,.2f}"],
        ["Conservative (P75)", f"€{confidence_bands.get('P75', 0):,.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Bill of Quantities
    story.append(Paragraph("Bill of Quantities", styles['Heading2']))
    
    boq_data = [["Material", "Quantity", "Unit", "Unit Price (EUR)", "Total (EUR)"]]
    
    for item in results.get("boq_items", []):
        boq_data.append([
            item["material_name"],
            str(item["quantity"]),
            item["unit"],
            f"€{item['unit_price']:.2f}",
            f"€{item['total_price']:,.2f}"
        ])
    
    boq_table = Table(boq_data, colWidths=[2.5*inch, 0.8*inch, 0.6*inch, 1*inch, 1.1*inch])
    boq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(boq_table)
    
    doc.build(story)
    return filename

def generate_csv_report(estimate: models.Estimate):
    """Generate CSV report for estimate"""
    
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/estimate_{estimate.id}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow(["Material", "Quantity", "Unit", "Unit Price (EUR)", "Total Price (EUR)", "Seasonal Factor"])
        
        # BoQ items
        for item in estimate.results.get("boq_items", []):
            writer.writerow([
                item["material_name"],
                item["quantity"],
                item["unit"],
                item["unit_price"],
                item["total_price"],
                item["seasonal_factor"]
            ])
    
    return filename