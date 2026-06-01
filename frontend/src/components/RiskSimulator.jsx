import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
// import axiosClient from '../api/axiosClient';
import predictionService from '../services/predictionService';

const RiskSimulator = () => {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const onSubmit = async (data) => {
    setLoading(true);
    setResult(null);
    try {
      const payload = {
        iyear: parseInt(data.iyear, 10),
        region: parseInt(data.region, 10),
        country: parseInt(data.country, 10),
        attacktype1: parseInt(data.attacktype1, 10),
        targtype1: parseInt(data.targtype1, 10),
        weaptype1: parseInt(data.weaptype1, 10),
      };

      // Gọi API qua Service (hiện đang dùng MockData)
      const response = await predictionService.predictRisk(payload);
      
      // Theo chuẩn API: response trả về là { data: { success_probability, risk_level } }
      if (response && response.data) {
        setResult(response.data);
      }
    } catch (error) {
      console.error("API Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-50 py-10 font-sans">
      <div className="max-w-7xl mx-auto px-6 md:px-10 space-y-8">
        
        {/* Header */}
        <div>
          <h2 className="text-3xl font-bold text-slate-900 tracking-tight">AI Risk Simulator</h2>
          <p className="text-slate-500 mt-2 max-w-3xl">
            Input geographical and tactical parameters to simulate the success probability of a hypothetical event. 
            Our Machine Learning model evaluates these factors against historical baselines.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Form Section */}
          <div className="lg:col-span-2 bg-white p-8 rounded-2xl shadow-sm border border-slate-100">
            <h3 className="text-xl font-semibold text-slate-800 mb-6 border-b border-slate-100 pb-4">Simulation Parameters</h3>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                
                {/* Year */}
                <div className="flex flex-col">
                  <label className="text-sm font-medium text-slate-700 mb-1">Target Year</label>
                  <input
                    type="number"
                    placeholder="e.g., 2026"
                    className={`bg-slate-50 border px-4 py-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${errors.iyear ? 'border-red-400' : 'border-slate-200'}`}
                    {...register("iyear", { required: true })}
                  />
                  {errors.iyear && <span className="text-red-500 text-xs mt-1">This field is required</span>}
                </div>

                {/* Region */}
                <div className="flex flex-col">
                  <label className="text-sm font-medium text-slate-700 mb-1">Region Code</label>
                  <input
                    type="number"
                    placeholder="e.g., 10"
                    className={`bg-slate-50 border px-4 py-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${errors.region ? 'border-red-400' : 'border-slate-200'}`}
                    {...register("region", { required: true })}
                  />
                  {errors.region && <span className="text-red-500 text-xs mt-1">This field is required</span>}
                </div>

                {/* Country */}
                <div className="flex flex-col">
                  <label className="text-sm font-medium text-slate-700 mb-1">Country Code</label>
                  <input
                    type="number"
                    placeholder="e.g., 215"
                    className={`bg-slate-50 border px-4 py-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${errors.country ? 'border-red-400' : 'border-slate-200'}`}
                    {...register("country", { required: true })}
                  />
                  {errors.country && <span className="text-red-500 text-xs mt-1">This field is required</span>}
                </div>

                {/* Attack Type */}
                <div className="flex flex-col">
                  <label className="text-sm font-medium text-slate-700 mb-1">Attack Type Code</label>
                  <input
                    type="number"
                    placeholder="e.g., 3"
                    className={`bg-slate-50 border px-4 py-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${errors.attacktype1 ? 'border-red-400' : 'border-slate-200'}`}
                    {...register("attacktype1", { required: true })}
                  />
                  {errors.attacktype1 && <span className="text-red-500 text-xs mt-1">This field is required</span>}
                </div>

                {/* Target Type */}
                <div className="flex flex-col">
                  <label className="text-sm font-medium text-slate-700 mb-1">Target Type Code</label>
                  <input
                    type="number"
                    placeholder="e.g., 14"
                    className={`bg-slate-50 border px-4 py-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${errors.targtype1 ? 'border-red-400' : 'border-slate-200'}`}
                    {...register("targtype1", { required: true })}
                  />
                  {errors.targtype1 && <span className="text-red-500 text-xs mt-1">This field is required</span>}
                </div>

                {/* Weapon Type */}
                <div className="flex flex-col">
                  <label className="text-sm font-medium text-slate-700 mb-1">Weapon Type Code</label>
                  <input
                    type="number"
                    placeholder="e.g., 6"
                    className={`bg-slate-50 border px-4 py-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${errors.weaptype1 ? 'border-red-400' : 'border-slate-200'}`}
                    {...register("weaptype1", { required: true })}
                  />
                  {errors.weaptype1 && <span className="text-red-500 text-xs mt-1">This field is required</span>}
                </div>

              </div>

              <div className="pt-4 flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all shadow-md hover:shadow-lg flex items-center justify-center min-w-[200px]"
                >
                  {loading ? (
                    <>
                      <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-3"></span>
                      Simulating...
                    </>
                  ) : (
                    "Run AI Prediction"
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Result Widget Section */}
          <div className="lg:col-span-1 flex flex-col">
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 flex-1 flex flex-col items-center justify-center text-center">
              {!result && !loading && (
                <div className="text-slate-400 flex flex-col items-center">
                  <svg className="w-16 h-16 mb-4 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                  <p className="text-sm">Submit the parameters to see<br/>the AI predictive analysis.</p>
                </div>
              )}

              {loading && (
                <div className="flex flex-col items-center justify-center w-full h-full space-y-4">
                   <div className="w-12 h-12 border-4 border-slate-100 border-t-blue-600 rounded-full animate-spin"></div>
                   <p className="text-slate-500 text-sm font-medium animate-pulse">Model is computing risk factors...</p>
                </div>
              )}

              {result && !loading && (
                <div className={`w-full flex flex-col items-center justify-center p-8 rounded-2xl border-2 transition-all ${
                  result.risk_level === 'High Risk' ? 'bg-red-50 border-red-200' :
                  result.risk_level === 'Medium Risk' ? 'bg-amber-50 border-amber-200' :
                  'bg-emerald-50 border-emerald-200'
                }`}>
                  <h4 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-2">Simulated Success Probability</h4>
                  <div className={`text-6xl font-black mb-4 ${
                    result.risk_level === 'High Risk' ? 'text-red-600' :
                    result.risk_level === 'Medium Risk' ? 'text-amber-600' :
                    'text-emerald-600'
                  }`}>
                    {(result.success_probability * 100).toFixed(1)}%
                  </div>
                  <div className={`inline-flex px-4 py-1.5 rounded-full text-sm font-bold tracking-wide uppercase ${
                    result.risk_level === 'High Risk' ? 'bg-red-100 text-red-800' :
                    result.risk_level === 'Medium Risk' ? 'bg-amber-100 text-amber-800' :
                    'bg-emerald-100 text-emerald-800'
                  }`}>
                    {result.risk_level}
                  </div>
                  
                  {result.risk_level === 'High Risk' && (
                    <p className="mt-6 text-sm text-red-700/80 font-medium">
                      Critical warning: The specified tactical parameters align heavily with historically successful attack vectors. Immediate mitigation is advised.
                    </p>
                  )}
                  {result.risk_level === 'Low Risk' && (
                    <p className="mt-6 text-sm text-emerald-700/80 font-medium">
                      Low threat indication: These parameters do not strongly correlate with successful historical attacks. Standard security protocols apply.
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default RiskSimulator;
