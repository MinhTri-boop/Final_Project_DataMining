import React, { useState, useEffect, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
// import axiosClient from '../api/axiosClient';
import dashboardService from '../services/dashboardService';
// A beautifully styled custom tooltip for Recharts
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-slate-100 p-4 rounded-lg shadow-lg">
        <p className="font-semibold text-slate-800 mb-2">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm text-slate-600 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }}></span>
            <span className="font-medium">{entry.name}:</span>
            <span>{entry.value.toLocaleString()}</span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const Dashboard = () => {
  const [regionTxt, setRegionTxt] = useState('');
  const [countryTxt, setCountryTxt] = useState('');
  const [cubeData, setCubeData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (regionTxt) params.append('regionTxt', regionTxt);
      if (countryTxt) params.append('countryTxt', countryTxt);
      params.append('page', 0);
      params.append('size', 100);

      const response = await dashboardService.getCubeStats(params);
      
      // If backend returns actual data, use it.
      const content = response?.data?.content || [];
      if (content.length > 0) {
        setCubeData(content);
      } else {
        setCubeData([]);
      }
    } catch (error) {
      console.error("API Error:", error);
      setCubeData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFilter = (e) => {
    e.preventDefault();
    fetchStats();
  };

  // Aggregation Logic for Charts
  const regionChartData = useMemo(() => {
    const map = {};
    cubeData.forEach(item => {
      const region = item.region_txt || 'Unknown';
      map[region] = (map[region] || 0) + (item.support || item.event_count || 0);
    });
    return Object.keys(map)
      .map(key => ({ name: key, events: map[key] }))
      .sort((a, b) => b.events - a.events)
      .slice(0, 10); // Top 10 regions
  }, [cubeData]);

  const trendChartData = useMemo(() => {
    const map = {};
    cubeData.forEach(item => {
      const time = item.decade || item.iyear || 'Unknown';
      if (time === 'Unknown') return;
      map[time] = (map[time] || 0) + (item.total_casualties || 0);
    });
    return Object.keys(map)
      .sort()
      .map(key => ({ time: key, casualties: map[key] }));
  }, [cubeData]);

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-10 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Security Analytics</h1>
            <p className="text-slate-500 mt-1">Global Risk & Intelligence Dashboard</p>
          </div>
          
          {/* Filter Form Card */}
          <form onSubmit={handleFilter} className="bg-white p-2 rounded-xl shadow-sm border border-slate-200 flex flex-wrap md:flex-nowrap gap-2 items-center">
            <input 
              type="text" 
              placeholder="Region (e.g. Middle East)" 
              value={regionTxt}
              onChange={(e) => setRegionTxt(e.target.value)}
              className="px-4 py-2 bg-slate-50 border-none rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm w-full md:w-48"
            />
            <input 
              type="text" 
              placeholder="Country (e.g. Iraq)" 
              value={countryTxt}
              onChange={(e) => setCountryTxt(e.target.value)}
              className="px-4 py-2 bg-slate-50 border-none rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm w-full md:w-48"
            />
            <button 
              type="submit" 
              disabled={loading}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2 min-w-[120px]"
            >
              {loading ? (
                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              ) : (
                <>Filter Data</>
              )}
            </button>
          </form>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Bar Chart: Attacks by Region */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col hover:shadow-md transition-shadow">
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-slate-800">Total Incidents by Region</h3>
              <p className="text-sm text-slate-500">Comparing historical attack volumes across top territories.</p>
            </div>
            <div className="flex-1 w-full h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={regionChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} tickFormatter={(val) => val.length > 10 ? val.substring(0, 10) + '...' : val} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} tickFormatter={(val) => `${val / 1000}k`} />
                  <RechartsTooltip content={<CustomTooltip />} cursor={{ fill: '#f8fafc' }} />
                  <Bar dataKey="events" name="Incidents" fill="#2563eb" radius={[4, 4, 0, 0]} barSize={32} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Area Chart: Casualty Trends */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col hover:shadow-md transition-shadow">
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-slate-800">Global Casualty Trends</h3>
              <p className="text-sm text-slate-500">Historical progression of total casualties (killed + wounded).</p>
            </div>
            <div className="flex-1 w-full h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendChartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCasualties" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} tickFormatter={(val) => `${val / 1000}k`} />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="casualties" name="Casualties" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorCasualties)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};


export default Dashboard;
