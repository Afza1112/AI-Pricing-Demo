from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import models, schemas, database, pricing_engine
from database import get_db
import json
from datetime import datetime
import uuid
import os

app = FastAPI(title="AI Pricing & Sourcing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
models.Base.metadata.create_all(bind=database.engine)

@app.on_event("startup")
async def startup_event():
    """Initialize database with seed data"""
    db = next(get_db())
    database.seed_data(db)

@app.get("/")
async def root():
    return {"message": "AI Pricing & Sourcing API"}

@app.post("/estimate/run", response_model=schemas.EstimateResponse)
async def create_estimate(request: schemas.EstimateRequest, db: Session = Depends(get_db)):
    """Generate project estimate with pricing and supplier recommendations"""
    try:
        # Generate estimate using pricing engine
        estimate_data = pricing_engine.generate_estimate(request, db)
        
        # Save estimate to database
        db_estimate = models.Estimate(
            id=str(uuid.uuid4()),
            project_meta=request.dict(),
            results=estimate_data,
            created_at=datetime.utcnow()
        )
        db.add(db_estimate)
        db.commit()
        
        return schemas.EstimateResponse(
            id=db_estimate.id,
            **estimate_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/estimate/{estimate_id}", response_model=schemas.EstimateResponse)
async def get_estimate(estimate_id: str, db: Session = Depends(get_db)):
    """Retrieve saved estimate"""
    estimate = db.query(models.Estimate).filter(models.Estimate.id == estimate_id).first()
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    return schemas.EstimateResponse(
        id=estimate.id,
        **estimate.results
    )

@app.get("/catalog/items")
async def get_catalog_items(db: Session = Depends(get_db)):
    """Get material catalog"""
    materials = db.query(models.Material).all()
    return [schemas.MaterialResponse.from_orm(m) for m in materials]

@app.get("/vendors")
async def get_vendors(db: Session = Depends(get_db)):
    """Get vendor database"""
    vendors = db.query(models.Vendor).all()
    return [schemas.VendorResponse.from_orm(v) for v in vendors]

@app.get("/export/{estimate_id}.pdf")
async def export_pdf(estimate_id: str, db: Session = Depends(get_db)):
    """Export estimate as PDF"""
    estimate = db.query(models.Estimate).filter(models.Estimate.id == estimate_id).first()
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    # Generate PDF
    pdf_path = pricing_engine.generate_pdf_report(estimate)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"estimate_{estimate_id}.pdf")

@app.get("/export/{estimate_id}.csv")
async def export_csv(estimate_id: str, db: Session = Depends(get_db)):
    """Export estimate as CSV"""
    estimate = db.query(models.Estimate).filter(models.Estimate.id == estimate_id).first()
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")
    
    # Generate CSV
    csv_path = pricing_engine.generate_csv_report(estimate)
    return FileResponse(csv_path, media_type="text/csv", filename=f"estimate_{estimate_id}.csv")

@app.post("/files/upload")
async def upload_boq(file: UploadFile = File(...)):
    """Upload BoQ CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    # Process uploaded BoQ
    content = await file.read()
    # TODO: Parse CSV and return structured data
    return {"message": "File uploaded successfully", "filename": file.filename}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)