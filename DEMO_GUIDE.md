# AI Pricing & Sourcing Demo Guide

## Quick Start

### Option 1: Automated Setup (Recommended)
1. Double-click `start-demo.bat`
2. Wait for both servers to start
3. Open http://localhost:3000 in your browser

### Option 2: Manual Setup
1. **Backend Setup:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn main:app --reload
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the Application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Demo Scenarios

### Scenario 1: Bridge Construction
- **Project Type:** Bridge
- **Location:** Athens, Greece
- **Size:** 1.5 lane-km
- **Start Month:** June (peak construction season)
- **Duration:** 18 months

**Expected Results:**
- Higher seasonal factors for summer months
- Concrete and steel as top cost drivers
- Multiple vendor recommendations with availability

### Scenario 2: Hotel Development
- **Project Type:** Hotel
- **Location:** Thessaloniki, Greece
- **Size:** 150 rooms
- **Start Month:** March (pre-season)
- **Duration:** 24 months
- **Advanced Options:** 4-star rating, 8 storeys

**Expected Results:**
- Lower seasonal pricing in early months
- Balanced material requirements
- Regional pricing differences

### Scenario 3: Business Park
- **Project Type:** Business Park
- **Location:** Patras, Greece
- **Size:** 20000 m²
- **Start Month:** September (post-summer)
- **Duration:** 15 months

**Expected Results:**
- Moderate seasonal adjustments
- Steel and concrete dominance
- Good vendor availability

## Key Features to Demonstrate

### 1. Parametric Estimation
- Show how different project types generate different BoQ templates
- Demonstrate size scaling effects
- Highlight material quantity calculations

### 2. Seasonal Pricing
- Compare estimates for different start months
- Show seasonal price factor charts
- Explain winter vs. summer construction impacts

### 3. Vendor Recommendations
- Multiple suppliers per material
- Stock availability indicators
- Lead time considerations
- Contact information

### 4. Confidence Bands
- P25/P50/P75 estimates
- Risk assessment
- Cost driver analysis

### 5. Export Functionality
- PDF report generation
- CSV data export
- Professional formatting

## Technical Architecture

### Backend (FastAPI)
- **Database:** SQLite with demo data
- **Pricing Engine:** Parametric models with seasonal adjustments
- **PDF Generation:** ReportLab for professional reports
- **API Documentation:** Automatic OpenAPI/Swagger

### Frontend (Next.js)
- **UI Framework:** React with TypeScript
- **Styling:** Tailwind CSS
- **Charts:** Recharts for data visualization
- **Forms:** React Hook Form with validation

### Data Model
- **Materials:** 10 construction materials with specifications
- **Price Indices:** 24 months of historical pricing
- **Seasonality:** Monthly adjustment factors
- **Vendors:** 5 suppliers with offers and availability
- **Estimates:** Saved project calculations

## Demo Data

### Materials Included
- Concrete C30/37
- Steel Rebar B500C
- Structural Steel S355
- Cement CEM I 42.5
- Bitumen 50/70
- Aggregate 0-32mm
- Formwork Plywood
- Skilled Labor
- General Labor
- Equipment Rental

### Vendor Network
- Hellenic Concrete Co. (Athens)
- Steel Masters SA (Thessaloniki)
- Mediterranean Aggregates (Patras)
- Athens Construction Supply
- Northern Equipment Rental

## Customization Options

### Adding New Materials
1. Update `database.py` seed data
2. Add to project templates in `pricing_engine.py`
3. Configure seasonal patterns

### New Project Types
1. Define parametric model in `PROJECT_TEMPLATES`
2. Add form options in frontend
3. Update validation schemas

### Regional Expansion
1. Add location factors in pricing engine
2. Expand vendor database
3. Include regional price indices

## Troubleshooting

### Common Issues
1. **Port conflicts:** Change ports in configuration files
2. **Database errors:** Delete `pricing_demo.db` to reset
3. **CORS issues:** Check frontend API URL configuration
4. **PDF generation:** Ensure reports directory exists

### Performance Notes
- Demo uses SQLite for simplicity
- Production should use PostgreSQL
- Consider caching for price calculations
- Implement pagination for large datasets

## Next Steps (Post-Demo)

### Production Enhancements
- Live supplier API integrations
- Real-time commodity pricing feeds
- Advanced forecasting models
- Multi-currency support
- User authentication and roles
- Project collaboration features
- Mobile responsiveness
- Advanced analytics dashboard

### Integration Possibilities
- ERP system connections
- Procurement platform APIs
- Project management tools
- Financial reporting systems
- Supply chain management
- Risk assessment modules