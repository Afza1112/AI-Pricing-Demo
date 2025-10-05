'use client';

import { EstimateResponse } from '@/types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Download, FileText, Table } from 'lucide-react';

interface EstimateResultsProps {
  estimate: EstimateResponse;
  onExportPDF: () => void;
  onExportCSV: () => void;
}

export default function EstimateResults({ estimate, onExportPDF, onExportCSV }: EstimateResultsProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Prepare seasonal chart data
  const seasonalData = Array.from({ length: 12 }, (_, i) => {
    const month = i + 1;
    const monthData = estimate.seasonal_chart_data.filter(d => d.month === month);
    const avgFactor = monthData.reduce((sum, d) => sum + d.price_factor, 0) / (monthData.length || 1);
    
    return {
      month: new Date(2024, i, 1).toLocaleString('default', { month: 'short' }),
      factor: avgFactor,
    };
  });

  return (
    <div className="space-y-6">
      {/* Cost Summary */}
      <div className="card">
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-xl font-semibold">Cost Summary</h2>
          <div className="flex space-x-2">
            <button
              onClick={onExportPDF}
              className="btn-secondary flex items-center space-x-2"
            >
              <FileText className="w-4 h-4" />
              <span>PDF</span>
            </button>
            <button
              onClick={onExportCSV}
              className="btn-secondary flex items-center space-x-2"
            >
              <Table className="w-4 h-4" />
              <span>CSV</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(estimate.confidence_bands.P25)}
            </div>
            <div className="text-sm text-green-700">Optimistic (P25)</div>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-3xl font-bold text-blue-600">
              {formatCurrency(estimate.confidence_bands.P50)}
            </div>
            <div className="text-sm text-blue-700">Most Likely (P50)</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {formatCurrency(estimate.confidence_bands.P75)}
            </div>
            <div className="text-sm text-orange-700">Conservative (P75)</div>
          </div>
        </div>
      </div>

      {/* Bill of Quantities */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Bill of Quantities</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Material
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Unit Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Seasonal Factor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {estimate.boq_items.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.material_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.quantity.toLocaleString()} {item.unit}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatCurrency(item.unit_price)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      item.seasonal_factor > 1 
                        ? 'bg-red-100 text-red-800' 
                        : item.seasonal_factor < 1 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {(item.seasonal_factor * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {formatCurrency(item.total_price)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Seasonal Price Factors */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Seasonal Price Factors</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={seasonalData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'Price Factor']} />
              <Line type="monotone" dataKey="factor" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top Cost Drivers */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Top Cost Drivers</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={estimate.cost_drivers}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="material" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip formatter={(value: number) => [formatCurrency(value), 'Cost']} />
              <Bar dataKey="cost" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Vendor Recommendations */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Vendor Recommendations</h3>
        <div className="space-y-6">
          {Object.entries(estimate.vendor_recommendations).map(([material, vendors]) => (
            <div key={material}>
              <h4 className="font-medium text-gray-900 mb-3">{material}</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {vendors.map((vendor, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h5 className="font-medium text-gray-900">{vendor.vendor_name}</h5>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        vendor.stock_status === 'In Stock' 
                          ? 'bg-green-100 text-green-800'
                          : vendor.stock_status === 'Limited Stock'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {vendor.stock_status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>Location: {vendor.location}</div>
                      <div>Price: {formatCurrency(vendor.price)}</div>
                      <div>Lead Time: {vendor.lead_time_days} days</div>
                      <div>MOQ: {vendor.moq.toLocaleString()}</div>
                      <div>Contact: {vendor.contact}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Assumptions */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Assumptions</h3>
        <ul className="list-disc list-inside space-y-2 text-sm text-gray-600">
          {estimate.assumptions.map((assumption, index) => (
            <li key={index}>{assumption}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}