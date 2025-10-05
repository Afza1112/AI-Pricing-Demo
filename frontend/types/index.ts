export interface EstimateRequest {
  project_type: 'bridge' | 'hotel' | 'business_park';
  location: string;
  size: number;
  size_unit: string;
  start_month: number;
  duration_months: number;
  structural_class?: string;
  star_rating?: number;
  storey_count?: number;
  facade_type?: string;
  concrete_class?: string;
  rebar_grade?: string;
  earthworks_volume?: number;
  preferred_vendors?: string[];
}

export interface BoQItem {
  material_name: string;
  quantity: number;
  unit: string;
  unit_price: number;
  total_price: number;
  seasonal_factor: number;
  confidence_band: {
    P25: number;
    P50: number;
    P75: number;
  };
}

export interface VendorRecommendation {
  vendor_name: string;
  location: string;
  price: number;
  stock_status: string;
  lead_time_days: number;
  moq: number;
  contact: string;
}

export interface EstimateResponse {
  id: string;
  boq_items: BoQItem[];
  total_cost: number;
  confidence_bands: {
    P25: number;
    P50: number;
    P75: number;
  };
  vendor_recommendations: Record<string, VendorRecommendation[]>;
  seasonal_chart_data: Array<{
    month: number;
    material: string;
    price_factor: number;
    price: number;
  }>;
  assumptions: string[];
  cost_drivers: Array<{
    material: string;
    cost: number;
    percentage: number;
  }>;
}

export interface Material {
  id: number;
  name: string;
  unit: string;
  category: string;
  spec: string;
}

export interface Vendor {
  id: number;
  name: string;
  region: string;
  contacts: Record<string, any>;
  reliability_score: number;
}