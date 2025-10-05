# AI Pricing & Sourcing Demo

A lightweight web application for construction project cost estimation with seasonal pricing and supplier recommendations.

## Features

- **Project Templates**: Bridge, Hotel, Business Park
- **Smart Pricing**: Seasonal adjustments and regional factors
- **Supplier Matching**: Availability, lead times, and pricing
- **Export Options**: PDF reports and CSV data
- **Confidence Bands**: P25/P50/P75 estimates

## Quick Start

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

## Architecture

- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Pricing Engine**: Python with seasonal adjustments
- **Export**: PDF generation with ReportLab

## Demo Data

The application includes seed data for:
- 3 project templates (Bridge, Hotel, Business Park)
- Material catalogs with seasonal pricing
- Vendor database with availability
- Sample estimates

## API Endpoints

- `POST /estimate/run` - Generate project estimate
- `GET /estimate/{id}` - Retrieve saved estimate
- `GET /catalog/items` - Material catalog
- `GET /vendors` - Vendor database
- `GET /export/{id}.pdf` - Export PDF report