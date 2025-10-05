'use client';

import { useState } from 'react';
import EstimateForm from '@/components/EstimateForm';
import EstimateResults from '@/components/EstimateResults';
import { EstimateRequest, EstimateResponse } from '@/types';
import { estimateAPI } from '@/lib/api';
import { AlertCircle, CheckCircle } from 'lucide-react';

export default function Home() {
  const [estimate, setEstimate] = useState<EstimateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (data: EstimateRequest) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await estimateAPI.create(data);
      setEstimate(result);
      setSuccess('Estimate generated successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate estimate');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = async () => {
    if (!estimate) return;

    try {
      const blob = await estimateAPI.exportPDF(estimate.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `estimate_${estimate.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      setSuccess('PDF exported successfully!');
    } catch (err) {
      setError('Failed to export PDF');
    }
  };

  const handleExportCSV = async () => {
    if (!estimate) return;

    try {
      const blob = await estimateAPI.exportCSV(estimate.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `estimate_${estimate.id}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      setSuccess('CSV exported successfully!');
    } catch (err) {
      setError('Failed to export CSV');
    }
  };

  const handleNewEstimate = () => {
    setEstimate(null);
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI Pricing & Sourcing Demo
        </h1>
        <p className="text-lg text-gray-600">
          Construction project cost estimation with seasonal pricing and supplier recommendations
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <CheckCircle className="h-5 w-5 text-green-400" />
            <div className="ml-3">
              <p className="text-sm text-green-800">{success}</p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      {!estimate ? (
        <EstimateForm onSubmit={handleSubmit} loading={loading} />
      ) : (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Estimate Results</h2>
            <button
              onClick={handleNewEstimate}
              className="btn-secondary"
            >
              New Estimate
            </button>
          </div>
          <EstimateResults
            estimate={estimate}
            onExportPDF={handleExportPDF}
            onExportCSV={handleExportCSV}
          />
        </div>
      )}

      {/* Demo Information */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Demo Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
          <div>
            <h4 className="font-medium mb-2">Project Templates</h4>
            <ul className="list-disc list-inside space-y-1">
              <li>Bridge construction</li>
              <li>Hotel development</li>
              <li>Business park</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">Smart Pricing</h4>
            <ul className="list-disc list-inside space-y-1">
              <li>Seasonal price adjustments</li>
              <li>Regional factors</li>
              <li>Confidence bands (P25/P50/P75)</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">Supplier Matching</h4>
            <ul className="list-disc list-inside space-y-1">
              <li>Stock availability</li>
              <li>Lead times</li>
              <li>Minimum order quantities</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">Export Options</h4>
            <ul className="list-disc list-inside space-y-1">
              <li>PDF reports</li>
              <li>CSV data export</li>
              <li>Shareable estimates</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}