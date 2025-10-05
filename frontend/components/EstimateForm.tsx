'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { EstimateRequest } from '@/types';
import { ChevronDownIcon, ChevronUpIcon } from 'lucide-react';

interface EstimateFormProps {
  onSubmit: (data: EstimateRequest) => void;
  loading: boolean;
}

export default function EstimateForm({ onSubmit, loading }: EstimateFormProps) {
  const [isAdvanced, setIsAdvanced] = useState(false);
  const { register, handleSubmit, watch, formState: { errors } } = useForm<EstimateRequest>();

  const projectType = watch('project_type');

  const getSizeUnit = (type: string) => {
    switch (type) {
      case 'bridge': return 'lane-km';
      case 'hotel': return 'rooms';
      case 'business_park': return 'm²';
      default: return 'm²';
    }
  };

  const getSizePlaceholder = (type: string) => {
    switch (type) {
      case 'bridge': return 'e.g., 1.5 (lane-kilometers)';
      case 'hotel': return 'e.g., 150 (number of rooms)';
      case 'business_park': return 'e.g., 20000 (square meters)';
      default: return 'Enter size';
    }
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-6">Project Estimation</h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="label">Project Type *</label>
            <select
              {...register('project_type', { required: 'Project type is required' })}
              className="input-field"
            >
              <option value="">Select project type</option>
              <option value="bridge">Bridge</option>
              <option value="hotel">Hotel</option>
              <option value="business_park">Business Park</option>
            </select>
            {errors.project_type && (
              <p className="text-red-500 text-sm mt-1">{errors.project_type.message}</p>
            )}
          </div>

          <div>
            <label className="label">Location *</label>
            <input
              type="text"
              {...register('location', { required: 'Location is required' })}
              placeholder="e.g., Athens, Greece"
              className="input-field"
            />
            {errors.location && (
              <p className="text-red-500 text-sm mt-1">{errors.location.message}</p>
            )}
          </div>

          <div>
            <label className="label">
              Size * {projectType && `(${getSizeUnit(projectType)})`}
            </label>
            <input
              type="number"
              step="0.1"
              {...register('size', { 
                required: 'Size is required',
                min: { value: 0.1, message: 'Size must be greater than 0' }
              })}
              placeholder={getSizePlaceholder(projectType)}
              className="input-field"
            />
            <input
              type="hidden"
              {...register('size_unit')}
              value={getSizeUnit(projectType)}
            />
            {errors.size && (
              <p className="text-red-500 text-sm mt-1">{errors.size.message}</p>
            )}
          </div>

          <div>
            <label className="label">Start Month *</label>
            <select
              {...register('start_month', { 
                required: 'Start month is required',
                valueAsNumber: true
              })}
              className="input-field"
            >
              <option value="">Select month</option>
              {Array.from({ length: 12 }, (_, i) => (
                <option key={i + 1} value={i + 1}>
                  {new Date(2024, i, 1).toLocaleString('default', { month: 'long' })}
                </option>
              ))}
            </select>
            {errors.start_month && (
              <p className="text-red-500 text-sm mt-1">{errors.start_month.message}</p>
            )}
          </div>

          <div>
            <label className="label">Duration (months) *</label>
            <input
              type="number"
              {...register('duration_months', { 
                required: 'Duration is required',
                valueAsNumber: true,
                min: { value: 1, message: 'Duration must be at least 1 month' }
              })}
              placeholder="e.g., 12"
              className="input-field"
            />
            {errors.duration_months && (
              <p className="text-red-500 text-sm mt-1">{errors.duration_months.message}</p>
            )}
          </div>
        </div>

        {/* Advanced Options Toggle */}
        <div className="border-t pt-4">
          <button
            type="button"
            onClick={() => setIsAdvanced(!isAdvanced)}
            className="flex items-center text-primary-600 hover:text-primary-700 font-medium"
          >
            {isAdvanced ? (
              <>
                <ChevronUpIcon className="w-4 h-4 mr-1" />
                Hide Advanced Options
              </>
            ) : (
              <>
                <ChevronDownIcon className="w-4 h-4 mr-1" />
                Show Advanced Options
              </>
            )}
          </button>
        </div>

        {/* Advanced Inputs */}
        {isAdvanced && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t">
            {projectType === 'bridge' && (
              <div>
                <label className="label">Structural Class</label>
                <select {...register('structural_class')} className="input-field">
                  <option value="">Select structural class</option>
                  <option value="prestressed">Prestressed Concrete</option>
                  <option value="post_tensioned">Post-tensioned</option>
                  <option value="steel_composite">Steel Composite</option>
                </select>
              </div>
            )}

            {projectType === 'hotel' && (
              <>
                <div>
                  <label className="label">Star Rating</label>
                  <select {...register('star_rating', { valueAsNumber: true })} className="input-field">
                    <option value="">Select star rating</option>
                    <option value={3}>3 Star</option>
                    <option value={4}>4 Star</option>
                    <option value={5}>5 Star</option>
                  </select>
                </div>
                <div>
                  <label className="label">Storey Count</label>
                  <input
                    type="number"
                    {...register('storey_count', { valueAsNumber: true })}
                    placeholder="e.g., 8"
                    className="input-field"
                  />
                </div>
              </>
            )}

            <div>
              <label className="label">Concrete Class</label>
              <select {...register('concrete_class')} className="input-field">
                <option value="">Select concrete class</option>
                <option value="C25/30">C25/30</option>
                <option value="C30/37">C30/37</option>
                <option value="C35/45">C35/45</option>
              </select>
            </div>

            <div>
              <label className="label">Rebar Grade</label>
              <select {...register('rebar_grade')} className="input-field">
                <option value="">Select rebar grade</option>
                <option value="B500A">B500A</option>
                <option value="B500B">B500B</option>
                <option value="B500C">B500C</option>
              </select>
            </div>

            <div>
              <label className="label">Earthworks Volume (m³)</label>
              <input
                type="number"
                step="0.1"
                {...register('earthworks_volume', { valueAsNumber: true })}
                placeholder="e.g., 5000"
                className="input-field"
              />
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end pt-6 border-t">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating Estimate...' : 'Generate Estimate'}
          </button>
        </div>
      </form>
    </div>
  );
}