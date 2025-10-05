import axios from 'axios';
import { EstimateRequest, EstimateResponse, Material, Vendor } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const estimateAPI = {
  create: async (request: EstimateRequest): Promise<EstimateResponse> => {
    const response = await api.post('/estimate/run', request);
    return response.data;
  },

  get: async (id: string): Promise<EstimateResponse> => {
    const response = await api.get(`/estimate/${id}`);
    return response.data;
  },

  exportPDF: async (id: string): Promise<Blob> => {
    const response = await api.get(`/export/${id}.pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  exportCSV: async (id: string): Promise<Blob> => {
    const response = await api.get(`/export/${id}.csv`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export const catalogAPI = {
  getMaterials: async (): Promise<Material[]> => {
    const response = await api.get('/catalog/items');
    return response.data;
  },
};

export const vendorAPI = {
  getVendors: async (): Promise<Vendor[]> => {
    const response = await api.get('/vendors');
    return response.data;
  },
};

export const fileAPI = {
  uploadBoQ: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default api;